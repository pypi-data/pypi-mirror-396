import math
from typing import Any, Optional

import dgl
import torch
import torch.nn.functional as F
from einops.layers.torch import Rearrange
from timm.models.vision_transformer import Attention, Mlp
from torch import nn

from flowgym import FGTensor
from flowgym.molecules import FGGraph
from flowgym.utils import append_dims

# Graph neural network

class GNN(nn.Module):
    """Timestep-dependent graph neural network (GNN).

    Uses graph convolutions with FiLM conditioning on time embeddings to
    predict value functions for molecular graphs.

    Parameters
    ----------
    node_feats : int
        Number of input node features.
    edge_feats : int
        Number of input edge features.
    hidden_dim : int, optional
        Hidden dimension for graph convolutions, by default 256.
    cond_dim : int, optional
        Conditioning dimension for FiLM layers, by default 256.
    depth : int, optional
        Number of residual graph blocks, by default 6.
    window_size : float, optional
        Window size for sinusoidal time embedding, by default 1000.0.
    t_mult : float, optional
        Multiplier for time values, by default 1000.0.
    """

    def __init__(
        self,
        node_feats: int,
        edge_feats: int,
        hidden_dim: int = 256,
        cond_dim: int = 256,
        depth: int = 6,
        window_size: float = 1000.0,
        t_mult: float = 1000.0,
        scale: float = 1.0,
        target_index: Optional[str] = None,
        target_mean: float = 0.0,
        target_std: float = 1.0,
    ):
        super().__init__()

        self.target_index = target_index
        self.target_mean = target_mean
        self.target_std = target_std

        if target_index is not None:
            node_feats += 1

        self.in_conv = dgl.nn.GraphConv(node_feats, hidden_dim)  # type: ignore
        self.edge_linear = nn.Linear(edge_feats, hidden_dim)
        self.time_embed = SinusoidalTimeEmbedding(128, cond_dim, window_size, t_mult)

        blocks = []
        for _ in range(depth):
            blocks.append(GraphResBlock(hidden_dim, hidden_dim, cond_dim))
        self.blocks = nn.ModuleList(blocks)

        self.head = nn.Linear(hidden_dim, 1)
        self.scale = scale

        nn.init.zeros_(self.head.weight)
        nn.init.zeros_(self.head.bias)

    def forward(self, x: FGGraph, t: torch.Tensor, **kwargs: Any) -> torch.Tensor:
        """Forward pass through the graph neural network.

        Parameters
        ----------
        x : FGGraph, batch size n
            Input molecular graph with node and edge features.
        t : torch.Tensor, shape (n,)
            Time step.

        Returns
        -------
        output : torch.Tensor, shape (n, 1)
            Predicted values.
        """
        g = x.graph
        n_index = x.n_idx

        cond = self.time_embed(t)

        with g.local_scope():
            h = torch.cat([g.ndata["a_t"], g.ndata["c_t"], g.ndata["x_t"]], dim=-1)  # type: ignore

            if self.target_index is not None:
                target = kwargs.get(self.target_index, None)
                if target is None:
                    raise ValueError("Target values must be provided when target_index is set.")

                target = target.to(h.device)
                target = (target - self.target_mean) / self.target_std
                h = torch.cat([h, target[n_index].unsqueeze(-1)], dim=-1)

            h = self.in_conv(g, h)

            # Add edge feature to initial representation
            g.edata["e"] = self.edge_linear(g.edata["e_t"])

            g.update_all(
                dgl.function.copy_e("e", "m"),
                dgl.function.mean("m", "e_mean")  # type: ignore
            )
            h += g.ndata["e_mean"]

            for block in self.blocks:
                h = block(g, h, cond, n_index)

            g.ndata["h"] = h
            h = dgl.readout_nodes(g, "h", op="mean")
            return self.scale * self.head(h)


class GraphResBlock(nn.Module):
    """Residual block for graph neural networks with FiLM conditioning.

    Parameters
    ----------
    in_dim : int
        Input feature dimension.
    out_dim : int
        Output feature dimension.
    cond_dim : int
        Conditioning dimension for FiLM layers.
    """

    def __init__(self, in_dim: int, out_dim: int, cond_dim: int):
        super().__init__()
        self.conv1 = dgl.nn.GraphConv(in_dim, out_dim)  # type: ignore
        self.norm1 = nn.LayerNorm(out_dim)
        self.film1 = GraphFiLM(out_dim, cond_dim)

        self.conv2 = dgl.nn.GraphConv(out_dim, out_dim)  # type: ignore
        self.norm2 = nn.LayerNorm(out_dim)
        self.film2 = GraphFiLM(out_dim, cond_dim)

        self.skip = nn.Linear(in_dim, out_dim) if in_dim != out_dim else nn.Identity()

    def forward(
        self,
        g: dgl.DGLGraph,
        x: torch.Tensor,
        cond: torch.Tensor,
        n_index: torch.Tensor,
    ) -> torch.Tensor:
        """Forward pass through the graph residual block.

        Parameters
        ----------
        g : dgl.DGLGraph, batch size n
            Input graph.
        x : torch.Tensor, shape (num_nodes, in_dim)
            Node features.
        cond : torch.Tensor, shape (n, cond_dim)
            Conditioning embeddings.
        n_index : torch.Tensor, shape (num_nodes,)
            Node-to-graph index mapping.

        Returns
        -------
        output : torch.Tensor, shape (num_nodes, out_dim)
            Output node features.
        """
        h = self.conv1(g, x)
        h = self.norm1(h)
        h = self.film1(h, cond, n_index)
        h = F.silu(h)

        h = self.conv2(g, x)
        h = self.norm2(h)
        h = self.film2(h, cond, n_index)
        h = F.silu(h)

        return h + self.skip(x)


class GraphFiLM(nn.Module):
    r"""Feature-wise Linear Modulation for graph nodes.

    Applies affine transformation to node features based on conditioning:
    :math:`\text{output} = x * (1 + \gamma) + \beta`, where \gamma and \beta are derived from the
    conditioning vector.

    Parameters
    ----------
    dim : int
        Feature dimension.
    cond_dim : int
        Conditioning dimension.
    """

    def __init__(self, dim: int, cond_dim: int):
        super().__init__()
        self.to_scale_shift = nn.Linear(cond_dim, 2 * dim)

    def forward(self, x: torch.Tensor, cond: torch.Tensor, n_index: torch.Tensor) -> torch.Tensor:
        """Apply FiLM modulation to graph node features.

        Parameters
        ----------
        x : torch.Tensor, shape (num_nodes, dim).
            Node features.
        cond : torch.Tensor, shape (batch_size, cond_dim)
            Conditioning embeddings.
        n_index : torch.Tensor, shape (num_nodes,)
            Node-to-graph index mapping.

        Returns
        -------
        output : torch.Tensor, shape (num_nodes, dim)
            Modulated features.
        """
        gamma, beta = self.to_scale_shift(cond).chunk(2, dim=-1)
        gamma = gamma[n_index]
        beta = beta[n_index]
        return x * (1 + gamma) + beta


class SinusoidalTimeEmbedding(nn.Module):
    """Sinusoidal time embedding followed by MLP.

    Embeds scalar time values into high-dimensional space using sinusoidal functions at different
    frequencies, then processes through an MLP.

    Parameters
    ----------
    dim : int, default=128
        Dimension of sinusoidal embedding.
    hidden_dim : int, default=256
        Hidden dimension of MLP.
    window_size : float, default=1000
        Maximum frequency for sinusoidal encoding.
    t_mult : float, default=1000
        Multiplier to scale time from [0, 1] to [0, t_mult].
    """

    def __init__(
        self,
        dim: int = 128,
        hidden_dim: int = 256,
        window_size: float = 1000.0,
        t_mult: float = 1000.0,
    ):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )

        self.t_mult = t_mult
        half = dim // 2
        freqs = torch.exp(-math.log(window_size) * torch.arange(half, dtype=torch.float32) / half)
        self.register_buffer("freqs", freqs)

    def forward(self, t: torch.Tensor) -> torch.Tensor:
        """Embed time values into high-dimensional space.

        Parameters
        ----------
        t : torch.Tensor, shape (n,)
            Time values in [0, 1].

        Returns
        -------
        output : torch.Tensor, shape (n, hidden_dim)
            Time embeddings.
        """
        t = t.float() * self.t_mult
        args = t.unsqueeze(-1) * self.freqs.unsqueeze(-2)
        emb = torch.cat([torch.sin(args), torch.cos(args)], dim=-1)
        return self.mlp(emb)

# Multi-layer perceptron

class MLP(nn.Module):
    """Multi-layer perceptron (MLP) with time conditioning.

    Parameters
    ----------
    in_dim : int
        Input dimension.
    out_dim : int
        Output dimension.
    time_dim : int, default=128
        Dimension of sinusoidal time embedding.
    cond_dim : int, default=256
        Conditioning dimension for FiLM layers.
    depth : int, default=3
        Number of hidden layers.
    width : int, default=256
        Width of hidden layers.
    window_size : float, default=1000
        Window size for time embedding.
    t_mult : float, default=1000
        Time multiplier for time embedding.
    """

    def __init__(
        self,
        in_dim: int,
        out_dim: int,
        time_dim: int = 128,
        cond_dim: int = 256,
        depth: int = 3,
        width: int = 256,
        window_size: float = 1000.0,
        t_mult: float = 1000.0,
    ) -> None:
        super().__init__()

        self.time_embed = SinusoidalTimeEmbedding(time_dim, cond_dim, window_size, t_mult)

        blocks = [Block(in_dim, width, cond_dim)]
        for _ in range(depth - 1):
            blocks.append(Block(width, width, cond_dim))

        self.blocks = nn.ModuleList(blocks)
        self.head = nn.Linear(width, out_dim, bias=True)

        nn.init.zeros_(self.head.weight)
        nn.init.zeros_(self.head.bias)

    def forward(
        self,
        x: FGTensor,
        t: torch.Tensor,
        **kwargs: Any,
    ) -> FGTensor:
        """Forward pass of the MLP.

        Parameters
        ----------
        x : torch.Tensor, shape (n, input_dim)
            Input data.
        t : torch.Tensor, shape (n,)
            Time steps, values in [0, 1].

        Returns
        -------
        output : torch.Tensor, shape (n, output_dim)
            Output of the MLP.
        """
        cond = self.time_embed(t)

        x_ = x.flatten(start_dim=t.ndim)
        for block in self.blocks:
            x_ = block(x_, cond)

        return FGTensor(self.head(x_).reshape(*x.shape[:-1], -1))


class Block(nn.Module):
    """A single block of the MLP with FiLM conditioning.

    Applies linear transformation, layer normalization, FiLM modulation, and SiLU activation.

    Parameters
    ----------
    in_dim : int
        Input feature dimension.
    out_dim : int
        Output feature dimension.
    cond_dim : int
        Conditioning dimension for FiLM layer.
    """

    def __init__(self, in_dim: int, out_dim: int, cond_dim: int):
        super().__init__()
        self.linear = nn.Linear(in_dim, out_dim)
        self.norm = nn.LayerNorm(out_dim)
        self.film = FiLM(out_dim, cond_dim)

    def forward(self, x: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        """Forward pass of the block.

        Parameters
        ----------
        x : torch.Tensor, shape (n, in_dim)
            Input features.
        cond : torch.Tensor, shape (n, cond_dim)
            Conditioning embeddings.

        Returns
        -------
        output : torch.Tensor, shape (n, out_dim)
            Output features.
        """
        return F.silu(self.film(self.norm(self.linear(x)), cond))


class FiLM(nn.Module):
    r"""Feature-wise Linear Modulation.

    Applies affine transformation: :math:`\text{output} = x * (1 + \gamma) + \beta`, where \gamma
    and \beta are predicted from conditioning information.

    Parameters
    ----------
    n_channels : int
        Number of feature channels.
    cond_dim : int
        Conditioning dimension.

    References
    ----------
    .. [1] Perez et al., "FiLM: Visual Reasoning with a General Conditioning Layer", AAAI 2018.
    """

    def __init__(self, n_channels: int, cond_dim: int):
        super().__init__()
        self.to_scale_shift = nn.Linear(cond_dim, 2 * n_channels, bias=True)

    def forward(self, x: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        """Apply FiLM modulation.

        Parameters
        ----------
        x : torch.Tensor, shape (n, n_channels)
            Input features.
        cond : torch.Tensor, shape (n, cond_dim)
            Conditioning vector.

        Returns
        -------
        output : torch.Tensor, shape (n, n_channels)
            Modulated features.
        """
        gamma, beta = self.to_scale_shift(cond).chunk(2, dim=-1)
        gamma = append_dims(gamma, x.ndim)
        beta = append_dims(beta, x.ndim)
        return x * (1 + gamma) + beta

# Convolutional neural network

class ConditionalSequential(nn.Module):
    def __init__(self, *layers):
        super().__init__()
        self.layers = nn.ModuleList(layers)

    def forward(self, x, c):
        for layer in self.layers:
            x = layer(x, c)
        return x


class CNN(nn.Module):
    """Convolutional Neural Network for image value prediction.

    Multi-stage CNN with residual blocks, FiLM conditioning, and global average pooling for
    predicting scalar values from images.

    Parameters
    ----------
    img_ch : int, default=3
        Number of input image channels.
    base_ch : int, default=64
        Base number of channels (doubled at each downsampling stage).
    cond_dim : int, default=4 * base_ch
        Conditioning dimension for FiLM layers.
    window_size : float, default=1000
        Window size for time embedding.
    t_mult : float, default=1000
        Time multiplier for time embedding.
    """

    def __init__(
        self,
        img_ch: int = 3,
        base_ch: int = 64,
        cond_dim: Optional[int] = None,
        num_blocks_per_stage: int = 1,
        window_size: float = 1000.0,
        t_mult: float = 1000.0,
        scale: int = 1,
        text_cond: bool = False,
    ):
        super().__init__()

        if cond_dim is None:
            cond_dim = 4 * base_ch

        self.time_embed = SinusoidalTimeEmbedding(128, cond_dim, window_size, t_mult)

        self.text_cond = text_cond
        if text_cond:
            self.text_embed = nn.Sequential(
                nn.Linear(768, cond_dim),
                nn.SiLU(),
                nn.Linear(cond_dim, cond_dim),
            )

        self.scale = scale
        self.in_conv = nn.Conv2d(img_ch, base_ch, 3, padding=1)

        self.stage1 = self._make_stage(base_ch, base_ch, cond_dim, num_blocks_per_stage, downsample=False)
        self.stage2 = self._make_stage(base_ch, 2 * base_ch, cond_dim, num_blocks_per_stage, downsample=True)
        self.stage3 = self._make_stage(2 * base_ch, 4 * base_ch, cond_dim, num_blocks_per_stage, downsample=True)

        self.gap = nn.AdaptiveAvgPool2d(1)
        self.out = nn.Sequential(
            nn.Flatten(),
            nn.Linear(base_ch * 4, 1)
        )

        nn.init.zeros_(self.out[-1].weight)
        nn.init.zeros_(self.out[-1].bias)


    def _make_stage(self, in_ch: int, out_ch: int, cond_dim: int, num_blocks: int, downsample: bool) -> nn.Module:
        blocks = []
        blocks.append(ConvResBlock(in_ch, out_ch, cond_dim, downsample=downsample))
        for _ in range(num_blocks-1):
            blocks.append(ConvResBlock(out_ch, out_ch, cond_dim, downsample=False))
        return ConditionalSequential(*blocks)

    def forward(self, x: FGTensor, t: torch.Tensor, **kwargs: Any) -> torch.Tensor:
        """Forward pass through the CNN.

        Parameters
        ----------
        x : FGTensor, shape (n, img_ch, height, width)
            Input images.
        t : torch.Tensor, shape (n,)
            Time steps.
        **kwargs : Any
            Additional keyword arguments (unused).

        Returns
        -------
        output : torch.Tensor, shape (n, 1)
            Predicted values.
        """
        cond = self.time_embed(t)
        if self.text_cond:
            assert "encoder_hidden_states" in kwargs, "Text conditioning enabled but no text embeddings provided."
            text_cond = kwargs["encoder_hidden_states"][:t.shape[0]]
            text_cond = text_cond.mean(dim=1)
            text_cond = self.text_embed(text_cond)
            cond = cond + text_cond
            # cond = torch.cat([cond, text_cond], dim=-1)

        h = self.in_conv(x)
        h = self.stage1(h, cond)
        h = self.stage2(h, cond)
        h = self.stage3(h, cond)
        h = self.gap(h)
        return self.scale * self.out(h)


class ConvResBlock(nn.Module):
    def __init__(self, in_ch: int, out_ch: int, cond_dim: int, downsample: bool = False):
        super().__init__()
        self.conv1 = nn.Conv2d(in_ch, out_ch, 3, padding=1, bias=False)
        self.gn1 = nn.GroupNorm(out_ch, out_ch)
        self.film1 = FiLM(out_ch, cond_dim)

        self.conv2 = nn.Conv2d(out_ch, out_ch, 3, padding=1, bias=False)
        self.gn2 = nn.GroupNorm(out_ch, out_ch)
        self.film2 = FiLM(out_ch, cond_dim)

        self.skip = (
            nn.Conv2d(in_ch, out_ch, 1)
            if in_ch != out_ch else nn.Identity()
        )
        self.down = BlurPool(out_ch) if downsample else nn.Identity()

    def forward(self, x: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        h = F.silu(self.film1(self.gn1(self.conv1(x)), cond))
        h = F.silu(self.film2(self.gn2(self.conv2(h)), cond))
        h = h + self.skip(x)
        h = self.down(h)
        return h


class BlurPool(nn.Module):
    """Anti-aliased 2x down-sampling.

    Applies a separable blur filter before subsampling to reduce aliasing artifacts during
    downsampling.

    Parameters
    ----------
    c : int
        Number of channels.
    filt : tuple of int, default=(1, 2, 1)
        1D filter coefficients.

    References
    ----------
    .. [1] Zhang, "Making Convolutional Networks Shift-Invariant Again",
           ICML 2019.
    """

    def __init__(self, c: int, filt=(1, 2, 1)):
        super().__init__()
        filt = torch.tensor(filt, dtype=torch.float32)
        kernel = filt[:, None] * filt[None, :]
        kernel /= kernel.sum()
        kernel = kernel[None, None, :, :].repeat(c, 1, 1, 1)
        self.register_buffer("kernel", kernel)
        self.pad = nn.ReflectionPad2d(1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply anti-aliased downsampling.

        Parameters
        ----------
        x : torch.Tensor, shape (n, c, height, width)
            Input feature maps.

        Returns
        -------
        output : torch.Tensor, shape (n, c, height//2, width//2)
            Downsampled feature maps.
        """
        x = self.pad(x)
        x = F.conv2d(x, self.kernel, stride=1, groups=x.shape[1])
        return x[:, :, ::2, ::2]


# Vision transformer


def pair(t):
    return t if isinstance(t, tuple) else (t, t)


def posemb_sincos_2d(h, w, dim, temperature: int = 10000, dtype = torch.float32):
    y, x = torch.meshgrid(torch.arange(h), torch.arange(w), indexing="ij")
    assert (dim % 4) == 0, "feature dimension must be multiple of 4 for sincos emb"
    omega = torch.arange(dim // 4) / (dim // 4 - 1)
    omega = 1.0 / (temperature ** omega)

    y = y.flatten()[:, None] * omega[None, :]
    x = x.flatten()[:, None] * omega[None, :]
    pe = torch.cat((x.sin(), x.cos(), y.sin(), y.cos()), dim=1)
    return pe.type(dtype)


def modulate(x, shift, scale):
    return x * (1 + scale.unsqueeze(1)) + shift.unsqueeze(1)



class ViTBlock(nn.Module):
    def __init__(self, dim, num_heads, mlp_ratio=4.0):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim, elementwise_affine=False, eps=1e-6)
        self.attn = Attention(dim, num_heads=num_heads, qkv_bias=True)
        self.norm2 = nn.LayerNorm(dim, elementwise_affine=False, eps=1e-6)
        self.mlp = Mlp(dim, int(dim * mlp_ratio))
        self.modulation = nn.Sequential(
            nn.SiLU(),
            nn.Linear(dim, 6 * dim, bias=True),
        )

        nn.init.zeros_(self.modulation[-1].weight)
        nn.init.zeros_(self.modulation[-1].bias)

    def forward(self, x, c):
        shift_msa, scale_msa, gate_msa, shift_mlp, scale_mlp, gate_mlp = self.modulation(c).chunk(6, dim=1)
        x = x + gate_msa.unsqueeze(1) * self.attn(modulate(self.norm1(x), shift_msa, scale_msa))
        x = x + gate_mlp.unsqueeze(1) * self.mlp(modulate(self.norm2(x), shift_mlp, scale_mlp))
        return x


class Transformer(nn.Module):
    def __init__(self, dim, depth, heads):
        super().__init__()
        self.blocks = nn.ModuleList([])
        for _ in range(depth):
            self.blocks.append(ViTBlock(dim, heads))

    def forward(self, x, c):
        for block in self.blocks:  # type: ignore
            x = block(x, c)

        return x


class ViT(nn.Module):
    def __init__(self, *, image_size, patch_size, dim, depth, heads, channels=3):
        super().__init__()
        image_height, image_width = pair(image_size)
        patch_height, patch_width = pair(patch_size)

        assert image_height % patch_height == 0 and image_width % patch_width == 0, 'Image dimensions must be divisible by the patch size.'

        patch_dim = channels * patch_height * patch_width

        self.to_patch_embedding = nn.Sequential(
            Rearrange("b c (h p1) (w p2) -> b (h w) (p1 p2 c)", p1 = patch_height, p2 = patch_width),
            nn.LayerNorm(patch_dim),
            nn.Linear(patch_dim, dim),
            nn.LayerNorm(dim),
        )

        self.pos_embedding = posemb_sincos_2d(
            h = image_height // patch_height,
            w = image_width // patch_width,
            dim = dim,
        )

        self.t_embedding =  SinusoidalTimeEmbedding(128, dim)
        self.transformer = Transformer(dim, depth, heads)

        self.pool = "mean"
        self.to_latent = nn.Identity()

        self.linear_head = nn.Linear(dim, 1)

        nn.init.zeros_(self.linear_head.weight)
        nn.init.zeros_(self.linear_head.bias)

    def forward(self, x: FGTensor, t: torch.Tensor, **kwargs: Any) -> torch.Tensor:
        device = x.device

        y = torch.as_tensor(x)
        y = self.to_patch_embedding(y)
        y += self.pos_embedding.to(device, dtype=y.dtype)
        c = self.t_embedding(t)

        y = self.transformer(y, c)
        y = y.mean(dim = 1)

        y = self.to_latent(y)
        return self.linear_head(y)
