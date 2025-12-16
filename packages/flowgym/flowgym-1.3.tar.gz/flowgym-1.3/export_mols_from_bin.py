#!/usr/bin/env python

import argparse
from pathlib import Path

import numpy as np

from dgl.data.utils import load_graphs
from rdkit import Chem
from rdkit.Chem import AllChem, Crippen, Descriptors, rdMolDescriptors, QED

# from your project
from flowmol.analysis.molecule_builder import SampledMolecule, atom_type_map


def is_connected(mol):
    """Return True if molecule is a single connected fragment."""
    try:
        frags = Chem.GetMolFrags(mol, asMols=False)
        return len(frags) == 1
    except Exception:
        return False


def ensure_3d(mol):
    """Return a 3D mol. If no conformer or flat Z, embed + quick optimize. None on failure."""
    if mol is None:
        return None
    try:
        needs_3d = (mol.GetNumConformers() == 0)
        if not needs_3d:
            conf = mol.GetConformer()
            zs = [conf.GetAtomPosition(i).z for i in range(mol.GetNumAtoms())]
            if (max(zs) - min(zs)) < 1e-4:
                needs_3d = True

        if needs_3d:
            mH = Chem.AddHs(mol)
            params = AllChem.ETKDGv3()
            params.randomSeed = 0xF00D
            if AllChem.EmbedMolecule(mH, params) != 0:
                return None
            try:
                if AllChem.MMFFHasAllMoleculeParams(mH):
                    AllChem.MMFFOptimizeMolecule(mH, maxIters=200)
                else:
                    AllChem.UFFOptimizeMolecule(mH, maxIters=200)
            except Exception:
                pass
            mol = Chem.RemoveHs(mH)
        return mol
    except Exception:
        return None


def validate_mol(mol: Chem.Mol) -> Chem.Mol:
    """Professor's validity check: returns validated mol or None if invalid."""
    try:
        Chem.RemoveStereochemistry(mol)
        Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
        Chem.AssignStereochemistryFrom3D(mol)

        for a in mol.GetAtoms():
            a.SetNoImplicit(True)
            if a.HasProp("_MolFileHCount"):
                a.ClearProp("_MolFileHCount")

        flags = Chem.SanitizeFlags.SANITIZE_ALL & ~Chem.SanitizeFlags.SANITIZE_ADJUSTHS
        err = Chem.SanitizeMol(mol, sanitizeOps=flags, catchErrors=True)
        if err:
            return None
        else:
            mol.UpdatePropertyCache(strict=True)
            return mol
    except Exception:
        return None


def write_mol_safe(mol, out_path: Path, overwrite=False) -> bool:
    """Atomic write to .mol; skip if exists unless overwrite."""
    try:
        out_path = out_path.with_suffix(".mol")
        if out_path.exists() and not overwrite:
            return True
        tmp = out_path.with_suffix(".mol.tmp")
        Chem.MolToMolFile(mol, str(tmp))
        tmp.replace(out_path)
        return True
    except Exception as e:
        print(f"[WARN] Write failed {out_path.name}: {e}")
        return False


def export_from_bin(bin_path: Path, outdir: Path, overwrite: bool = False):
    print(f"[INFO] Loading graphs from {bin_path}")
    graphs, _ = load_graphs(str(bin_path))
    print(f"[INFO] Loaded {len(graphs)} graphs")

    outdir.mkdir(parents=True, exist_ok=True)

    n_valid = 0
    for j, g in enumerate(graphs):
        try:
            sm = SampledMolecule(g, atom_type_map)
            rd = getattr(sm, "rdkit_mol", None)
            if rd is None:
                continue

            if not is_connected(rd):
                continue

            rd3d = ensure_3d(rd)
            if rd3d is None:
                continue

            rd_valid = validate_mol(Chem.Mol(rd3d))
            if rd_valid is None:
                continue

            # valid molecule – write .mol
            n_valid += 1
            out_name = f"{bin_path.stem}_idx_{j:03d}.mol"
            out_path = outdir / out_name
            write_mol_safe(rd_valid, out_path, overwrite=overwrite)
        except Exception as e:
            # just skip bad graphs
            print(f"[WARN] Failed on graph {j}: {e}")
            continue

    print(f"[INFO] Wrote {n_valid} valid .mol files to {outdir}")


def main():
    ap = argparse.ArgumentParser(description="Export RDKit .mol files from a DGL .bin samples file.")
    ap.add_argument("bin_file", help="Path to samples_X.bin")
    ap.add_argument(
        "--outdir",
        default="exported_mols",
        help="Output directory to store .mol files (default: exported_mols)",
    )
    ap.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing .mol files if they exist.",
    )
    args = ap.parse_args()

    bin_path = Path(args.bin_file).expanduser().resolve()
    outdir = Path(args.outdir).expanduser().resolve()

    if not bin_path.is_file():
        raise SystemExit(f"[ERROR] File not found: {bin_path}")

    export_from_bin(bin_path, outdir, overwrite=args.overwrite)


if __name__ == "__main__":
    main()
