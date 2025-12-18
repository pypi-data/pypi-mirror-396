# plink_utils


import os
import sys
import subprocess
import logging
from typing import Optional


def run_plink2(command: str):
    """
    Run a shell command invoking PLINK2, capturing stdout/stderr for logging.


    On non-zero exit, raise RuntimeError with PLINK2's stderr so callers
    fail fast instead of hitting missing .fam/.bed later.
    """
    logging.info("[plink_utils:run_plink2] %s", command)
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        logging.error(
            "[plink_utils:run_plink2] PLINK2 failed (code %d).\nSTDERR:\n%s\nSTDOUT:\n%s",
            result.returncode,
            stderr,
            stdout,
        )
        raise RuntimeError(
            f"PLINK2 failed (exit {result.returncode}).\n"
            f"Command: {command}\n"
            f"STDERR:\n{stderr}\n"
            f"STDOUT:\n{stdout}"
        )
    else:
        logging.debug(
            "[plink_utils:run_plink2] Output:\n%s", (result.stdout or "").strip()
        )


def _create_sorted_pgen_from_pedmap(
    plink2_path: str,
    ped_path: str,
    map_path: str,
    temp_prefix: str,
) -> None:
    """
    Fallback step for PLINK2 'split chromosome' errors.


    1) Take the already-written PED/MAP (per-measure, per-sex).
    2) Normalize variant ordering via --make-pgen --sort-vars.
    """
    logging.info(
        "[plink_utils:_create_sorted_pgen_from_pedmap] "
        "Making sorted PGEN from PED/MAP: ped=%s map=%s out=%s",
        ped_path,
        map_path,
        temp_prefix,
    )
    cmd = (
        f"{plink2_path} "
        f"--ped {ped_path} "
        f"--map {map_path} "
        f"--make-pgen --sort-vars "
        f"--out {temp_prefix}"
    )
    run_plink2(cmd)


def generate_bed_bim_fam(
    plink2_path: str,
    ped_file: str,
    map_file: str,
    output_prefix: str,
    relax_mind_threshold: bool = False,
    maf_threshold: Optional[float] = None,
    sample_keep_path: Optional[str] = None,
    autosomes_only: bool = False,
    reference_allele_path: Optional[str] = None,
):
    """
    Generates BED/BIM/FAM from PED/MAP using PLINK2, matching Hao's R:


        plink2 --pedmap <prefix> --make-bed --geno 0.1 --mind 0.1 --out <prefix>


    Notes:
      - Primary path: exactly the above, via --pedmap <output_prefix>.
      - Fallback: if PLINK2 complains about 'split chromosome',
        we normalize variants via --make-pgen --sort-vars, then
        re-run as:


            plink2 --pfile <temp_prefix> --make-bed ...


      - We still expect <output_prefix>.ped/.map to exist before calling.
      - If reference_allele_path is provided, we pass it through to PLINK2
        via --reference-allele <file>, mirroring Hao's new workflow.
    """
    ped_expect = f"{output_prefix}.ped"
    map_expect = f"{output_prefix}.map"

    if not os.path.exists(ped_expect):
        raise FileNotFoundError(f"Missing PED for --pedmap: {ped_expect}")
    if not os.path.exists(map_expect):
        raise FileNotFoundError(f"Missing MAP for --pedmap: {map_expect}")

    mind = "" if relax_mind_threshold else "--mind 0.1"
    maf = f"--maf {maf_threshold}" if maf_threshold is not None else ""  # usually None
    keep = f"--keep {sample_keep_path}" if sample_keep_path else ""  # usually none
    chrflag = "--chr 1-19" if autosomes_only else ""  # usually off
    ref = f"--reference-allele {reference_allele_path}" if reference_allele_path else ""

    logging.info(
        "[plink_utils:generate_bed_bim_fam] --pedmap %s -> BED with %s %s %s %s %s",
        output_prefix,
        mind or "no --mind",
        maf or "no --maf",
        keep or "no --keep",
        chrflag or "all chr",
        ref or "no --reference-allele",
    )

    try:
        # 1) Try Hao-style direct pedmap -> bed
        pedmap_cmd = (
            f"{plink2_path} --pedmap {output_prefix} "
            f"--make-bed --geno 0.1 {mind} {maf} {keep} {chrflag} {ref} --out {output_prefix}"
        )
        run_plink2(pedmap_cmd)
    except RuntimeError:
        logging.warning(
            "[plink_utils:generate_bed_bim_fam] PLINK2 reported an error. "
            "Falling back to make-pgen + sort-vars + pfile->bed pipeline."
        )

        # 2) Fallback: sorted PGEN pipeline
        temp_prefix = f"{output_prefix}_sorted"

        # Normalize variants from the per-measure PED/MAP (not the big reference files)
        _create_sorted_pgen_from_pedmap(
            plink2_path=plink2_path,
            ped_path=ped_expect,
            map_path=map_expect,
            temp_prefix=temp_prefix,
        )

        # Now convert sorted PGEN to BED/BIM/FAM with same filters
        pfile_cmd = (
            f"{plink2_path} --pfile {temp_prefix} "
            f"--make-bed --geno 0.1 {mind} {maf} {keep} {chrflag} {ref} "
            f"--out {output_prefix}"
        )
        run_plink2(pfile_cmd)

    # 3) Sanity-check that PLINK2 actually produced the expected BED/BIM/FAM
    fam_expect = f"{output_prefix}.fam"
    if not os.path.exists(fam_expect):
        raise FileNotFoundError(
            f"PLINK2 finished but FAM file not found: {fam_expect}. "
            "Check PLINK2 STDERR/STDOUT for details."
        )


def calculate_kinship_matrix(
    plink2_path: str,
    input_prefix: str,
    output_prefix: str,
    sample_keep_path: Optional[str] = None,
):
    """
    Create PLINK .rel kinship files from BED/BIM/FAM files:


        plink2 --bfile <input_prefix> --make-rel square --out <output_prefix>
    """
    keep = f"--keep {sample_keep_path}" if sample_keep_path else ""
    cmd = f"{plink2_path} --bfile {input_prefix} {keep} --make-rel square --out {output_prefix}"
    run_plink2(cmd)


def calculate_kinship_from_pedmap(
    plink2_path: str,
    pedmap_prefix: str,
    kin_prefix: str,
):
    """
    Compute kinship, preferring Hao-style --pedmap, with a minimal
    fallback for split-chromosome errors.


    Normal case (UCLA1 etc.):


        plink2 --pedmap <pedmap_prefix> --make-rel square --out <kin_prefix>


    If PLINK2 complains that the temporary .pvar has a split chromosome,
    we DO NOT re-make anything; we assume BED/BIM/FAM already exist for
    <pedmap_prefix> (because generate_bed_bim_fam already ran) and do:


        plink2 --bfile <pedmap_prefix> --make-rel square --out <kin_prefix>
    """
    try:
        # 1) Try the Hao-style pedmap call first
        cmd = (
            f"{plink2_path} --pedmap {pedmap_prefix} "
            f"--make-rel square --out {kin_prefix}"
        )
        run_plink2(cmd)
        return
    except Exception as e:
        msg = str(e)

        logging.warning(
            "[plink_utils:calculate_kinship_from_pedmap] PLINK2 failed on --pedmap. "
            "Falling back to existing BED/BIM/FAM if available. Error: %s",
            msg,
        )

    # 2) Fallback: we already have BED/BIM/FAM from generate_bed_bim_fam
    bed = pedmap_prefix + ".bed"
    bim = pedmap_prefix + ".bim"
    fam = pedmap_prefix + ".fam"

    logging.info(
        "[plink_utils:calculate_kinship_from_pedmap] "
        "Using existing BED/BIM/FAM: %s, %s, %s",
        bed,
        bim,
        fam,
    )
    logging.info(
        "[plink_utils:calculate_kinship_from_pedmap] "
        "folder that is suppoesed to contain them: %s",
        os.listdir(os.path.dirname(bed)),
    )
    if not (os.path.exists(bed) and os.path.exists(bim) and os.path.exists(fam)):
        raise RuntimeError(
            "[plink_utils:calculate_kinship_from_pedmap] Split-chromosome error from "
            "--pedmap, and BED/BIM/FAM not found for prefix "
            f"{pedmap_prefix!r}. Expected {bed}, {bim}, {fam}. "
            "This suggests generate_bed_bim_fam was not run or the prefixes differ."
        )

    # Use exactly the same variant set as association
    run_plink2(
        f"{plink2_path} --bfile {pedmap_prefix} "
        f"--make-rel square --out {kin_prefix}"
    )


def calculate_kinship_with_pylmm3(
    bfile_prefix: str,
    kin_output_path: Optional[str] = None,
    verbose: bool = True,
) -> None:
    """
    Compute kinship via pylmm3.scripts.pylmmKinship, mirroring Hao's usage:


        python pylmmKinship.py -v --bfile 45911.m 45911.m.kin


    Here we rely on pylmm3 being installed in the *same environment* as plinkformatter
    and invoke:


        python -m pylmm3.scripts.pylmmKinship -v --bfile <bfile_prefix> <kin_output_path>


    Args:
        bfile_prefix:  Base path for PLINK binary files (no extension).
        kin_output_path: Optional output path for kinship matrix. If None,
            defaults to '<bfile_prefix>.kin'.
        verbose: If True, pass '-v' to pylmm3.
    """
    if kin_output_path is None:
        kin_output_path = bfile_prefix + ".kin"

    cmd = [
        sys.executable,
        "-m",
        "pylmm3.scripts.pylmmKinship",
    ]
    if verbose:
        cmd.append("-v")
    cmd.extend(["--bfile", bfile_prefix, kin_output_path])

    logging.info(
        "[plink_utils:calculate_kinship_with_pylmm3] running: %s",
        " ".join(cmd),
    )
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        logging.error(
            "[plink_utils:calculate_kinship_with_pylmm3] pylmm3 kinship failed "
            "(code %d).\nSTDERR:\n%s\nSTDOUT:\n%s",
            result.returncode,
            stderr,
            stdout,
        )
        raise RuntimeError(
            f"pylmm3 kinship failed (exit {result.returncode}).\n"
            f"Command: {' '.join(cmd)}\n"
            f"STDERR:\n{stderr}\n"
            f"STDOUT:\n{stdout}"
        )

    logging.info(
        "[plink_utils:calculate_kinship_with_pylmm3] success, kinship written to %s",
        kin_output_path,
    )


def rewrite_pheno_ids_from_fam(pheno_path: str, fam_path: str, out_path: str) -> None:
    """
    Make PHENO rows match FAM in both order AND IID values (no de-duplication).
      - PHENO: FID IID zscore value   (we REPLACE IID with FAM's IID in FAM order)
      - FAM:   FID IID PID MID SEX PHE


    Counts must already match per FID if PED and PHENO were written together.
    """
    import pandas as pd

    fam = pd.read_csv(
        fam_path,
        sep=r"\s+",
        header=None,
        names=["FID", "IID", "PID", "MID", "SEX", "PHE"],
        engine="python",
    )
    phe = pd.read_csv(
        pheno_path,
        sep=r"\s+",
        header=None,
        names=["FID", "IID", "zscore", "value"],
        engine="python",
    )

    out_chunks = []
    phe_groups = {k: g for k, g in phe.groupby("FID", sort=False)}
    for fid, fam_grp in fam.groupby("FID", sort=False):
        if fid not in phe_groups:
            raise ValueError(f"FID present in FAM but missing in PHENO: {fid}")

        phe_grp = phe_groups[fid].copy()

        # Strict 1:1 check (DO NOT drop duplicates; we want exact replicate counts)
        if len(phe_grp) != len(fam_grp):
            raise ValueError(
                f"PHENO vs FAM row-count mismatch for FID={fid}: "
                f"pheno={len(phe_grp)} fam={len(fam_grp)}"
            )

        phe_grp = phe_grp.reset_index(drop=True)
        phe_grp["IID"] = fam_grp["IID"].reset_index(
            drop=True
        )  # copy FAM IIDs (with suffixes)
        out_chunks.append(phe_grp[["FID", "IID", "zscore", "value"]])

    out = pd.concat(out_chunks, axis=0)
    out.to_csv(out_path, sep=" ", header=False, index=False)
