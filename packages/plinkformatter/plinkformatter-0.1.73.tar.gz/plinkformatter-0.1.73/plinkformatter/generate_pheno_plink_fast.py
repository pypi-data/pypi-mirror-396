# generate_pheno_plink_fast.py  (explicit DO/NON-DO via panel_type)
from __future__ import annotations


import os
import math
import logging
from typing import Dict, List, Union, Optional, Tuple


import numpy as np
import pandas as pd
from statistics import NormalDist


from plinkformatter.plink_utils import (
    generate_bed_bim_fam,
    calculate_kinship_from_pedmap,
    calculate_kinship_with_pylmm3,
)


from plinkformatter.generate_pheno_plink import extract_pheno_measure


MIN_SAMPLES_FOR_KINSHIP: int = 50




def _norm_id(x) -> str:
    """
    Normalize IDs used to join DO PED V1 with pheno['animal_id'].
    - Strip whitespace.
    - If numeric, collapse "123", "123.0", "123.000" → "123".
    """
    s = str(x).strip()
    if s == "":
        return s
    try:
        f = float(s)
        if f.is_integer():
            return str(int(f))
        return ("%.10g" % f).rstrip()
    except Exception:
        if s.endswith(".0"):
            s = s[:-2]
        return s




def rz_transform(values: Union[pd.Series, np.ndarray, List[float]]) -> np.ndarray:
    """
    Match Hao's R:
      rankY = rank(y, ties.method="average", na.last="keep")
      rzT  = qnorm(rankY/(length(na.exclude(rankY))+1))


    Here:
      - ties -> average (pandas rank(method="average"))
      - NA keep
      - qnorm -> NormalDist().inv_cdf
    """
    arr = pd.Series(values, copy=False)
    # treat non-finite as NA (R's na.last="keep")
    v = pd.to_numeric(arr, errors="coerce").astype(float)
    mask = np.isfinite(v.to_numpy())
    out = np.full(v.shape[0], np.nan, dtype=float)


    if mask.sum() == 0:
        return out


    # ranks on non-NA only
    ranks = pd.Series(v.to_numpy()[mask]).rank(method="average", na_option="keep").to_numpy()
    n = int(mask.sum())
    p = ranks / (n + 1.0)


    nd = NormalDist()
    out_vals = np.array([nd.inv_cdf(pi) for pi in p], dtype=float)
    out[mask] = out_vals
    return out




# ----------------------------- NON-DO PATH ----------------------------- #
def generate_pheno_plink_fast_non_do(
    ped_file: str,
    map_file: str,
    pheno: pd.DataFrame,
    outdir: str,
) -> pd.DataFrame:
    """
    NON-DO matches Hao:


      - Join by strain
      - FID = strain
      - IID = strain_animal_id   (paste0(strain, "_", animal_id))
      - SEX: f->2, m->1
      - Write per-measure, per-sex:
          <meas>.<sex>.ped   (space-delimited)
          <meas>.<sex>.map   (tab-delimited)
          <meas>.<sex>.pheno (space-delimited):
              FID IID zscore value rankzonvalue
    """
    os.makedirs(outdir, exist_ok=True)
    if pheno is None or pheno.empty:
        return pd.DataFrame()


    need = ("strain", "sex", "measnum", "value", "animal_id")
    missing = [c for c in need if c not in pheno.columns]
    if missing:
        raise ValueError(f"[NON_DO] pheno missing required columns: {missing} (need {list(need)})")


    ph = pheno.copy()
    ph["strain"] = ph["strain"].astype(str).str.replace(" ", "", regex=False)
    ph = ph[ph["sex"].isin(["f", "m"])].copy()
    if ph.empty:
        return ph


    # MAP sanitize (Hao: "." -> chr_bp)
    map_df = pd.read_csv(map_file, header=None, sep=r"\s+", engine="python")
    map_df[1] = np.where(
        map_df[1].astype(str) == ".",
        map_df[0].astype(str) + "_" + map_df[3].astype(str),
        map_df[1].astype(str),
    )


    # Ensure zscore column exists (Hao writes it even if NA)
    if "zscore" not in ph.columns:
        ph["zscore"] = np.nan


    # Build strain -> byte offset index from reference PED
    ped_offsets: Dict[str, int] = {}
    with open(ped_file, "rb") as f:
        while True:
            pos = f.tell()
            line = f.readline()
            if not line:
                break
            first_tab = line.find(b"\t")
            fid_bytes = (line.strip().split()[0] if first_tab <= 0 else line[:first_tab])
            name = fid_bytes.decode(errors="replace").replace("?", "").replace(" ", "")
            if name and name not in ped_offsets:
                ped_offsets[name] = pos


    ped_strains = set(ped_offsets.keys())
    ph = ph[ph["strain"].isin(ped_strains)].reset_index(drop=True)
    if ph.empty:
        return ph


    # IMPORTANT: do NOT drop duplicates here; Hao does a left_join and keeps rows.
    # If your raw CSV truly has duplicates, Hao's pipeline would carry them too.


    for (measnum, sex), df in ph.groupby(["measnum", "sex"], sort=False):
        measnum = int(measnum)
        sex = str(sex)


        map_out = os.path.join(outdir, f"{measnum}.{sex}.map")
        map_df.to_csv(map_out, sep="\t", index=False, header=False)


        ped_out = os.path.join(outdir, f"{measnum}.{sex}.ped")
        phe_out = os.path.join(outdir, f"{measnum}.{sex}.pheno")


        # stable ordering: Hao's code ends up in ped strain order after join;
        # we keep stable, grouped by strain, but replicate rows remain.
        df = df.reset_index(drop=True)


        # compute rankz on value for THIS group (Hao does this inside write step)
        rankz = rz_transform(df["value"].to_numpy())
        df = df.copy()
        df["rankzonvalue"] = rankz


        with open(ped_out, "w", encoding="utf-8") as f_ped, open(phe_out, "w", encoding="utf-8") as f_ph:
            for strain, sdf in df.groupby("strain", sort=False):
                with open(ped_file, "rb") as fp:
                    fp.seek(ped_offsets[strain])
                    raw = fp.readline().decode(errors="replace").rstrip("\n")


                # support old tabbed-pair PED and new allele-per-column PED
                parts = raw.split("\t")
                if len(parts) <= 6:
                    parts = raw.split()
                if len(parts) < 7:
                    raise ValueError("Malformed PED: need >=7 columns (6 meta + genotypes)")


                geno_fields = parts[6:]
                needs_split = any(" " in gp for gp in geno_fields)
                if needs_split:
                    geno_tokens: List[str] = []
                    for gp in geno_fields:
                        a_b = gp.split()
                        if len(a_b) != 2:
                            raise ValueError(f"Genotype pair not splitable into two alleles: {gp!r}")
                        geno_tokens.extend(a_b)
                else:
                    geno_tokens = geno_fields


                for _, r in sdf.iterrows():
                    aid = _norm_id(r["animal_id"])
                    iid = f"{strain}_{aid}"


                    z = r.get("zscore", np.nan)
                    v = r.get("value", np.nan)
                    rz = r.get("rankzonvalue", np.nan)


                    try:
                        z = float(z)
                    except Exception:
                        z = np.nan
                    try:
                        v = float(v)
                    except Exception:
                        v = np.nan
                    try:
                        rz = float(rz)
                    except Exception:
                        rz = np.nan


                    sex_code = "2" if sex == "f" else "1"
                    # Hao uses V6 = rz.transform(value) in current util; set PHE to rankz
                    phe_code = f"{rz}" if math.isfinite(rz) else "-9"


                    meta = [strain, iid, "0", "0", sex_code, phe_code]
                    f_ped.write(" ".join(meta + geno_tokens) + "\n")


                    # pheno: FID IID zscore value rankzonvalue
                    f_ph.write(
                        f"{strain} {iid} "
                        f"{(z if math.isfinite(z) else -9)} "
                        f"{(v if math.isfinite(v) else -9)} "
                        f"{(rz if math.isfinite(rz) else -9)}\n"
                    )


        logging.info(f"[NON_DO] wrote {ped_out}, {map_out}, {phe_out}")


    return ph




# ------------------------------- DO PATH ------------------------------- #
def generate_pheno_plink_fast_do(
    ped_file: str,
    map_file: str,
    pheno: pd.DataFrame,
    outdir: str,
) -> pd.DataFrame:
    """
    DO matches Hao:
      - overlap by animal_id vs PED V1
      - order follows PED order
      - pheno file includes rankzonvalue like Hao
    """
    os.makedirs(outdir, exist_ok=True)
    if pheno is None or pheno.empty:
        return pd.DataFrame()


    need = ("strain", "sex", "measnum", "value", "animal_id")
    missing = [c for c in need if c not in pheno.columns]
    if missing:
        raise ValueError(f"[DO] pheno missing required columns: {missing} (need {list(need)})")


    ph = pheno.copy()
    ph["strain"] = ph["strain"].astype(str).str.replace(" ", "", regex=False)
    ph = ph[ph["sex"].isin(["f", "m"])].copy()
    ph["animal_id_norm"] = ph["animal_id"].map(_norm_id)
    ph = ph[ph["animal_id_norm"].notna() & (ph["animal_id_norm"] != "")].copy()
    if ph.empty:
        return ph


    map_df = pd.read_csv(map_file, header=None, sep=r"\s+", engine="python")
    map_df[1] = np.where(
        map_df[1].astype(str) == ".",
        map_df[0].astype(str) + "_" + map_df[3].astype(str),
        map_df[1].astype(str),
    )


    if "zscore" not in ph.columns:
        ph["zscore"] = np.nan


    # For each group build map: animal_id_norm -> (z, v, rz, sex)
    per_group_maps: Dict[Tuple[int, str], Dict[str, tuple]] = {}
    global_ids: set[str] = set()


    for (meas, sex), g in ph.groupby(["measnum", "sex"], sort=False):
        meas = int(meas)
        sex = str(sex)


        # keep first per animal_id_norm (Hao's match/slice behavior)
        g = g.drop_duplicates(subset=["animal_id_norm"], keep="first").copy()


        rz = rz_transform(g["value"].to_numpy())
        g["rankzonvalue"] = rz


        m: Dict[str, tuple] = {}
        for _, r in g.iterrows():
            aid = r["animal_id_norm"]
            z = r.get("zscore", np.nan)
            v = r.get("value", np.nan)
            rr = r.get("rankzonvalue", np.nan)
            try:
                z = float(z)
            except Exception:
                z = np.nan
            try:
                v = float(v)
            except Exception:
                v = np.nan
            try:
                rr = float(rr)
            except Exception:
                rr = np.nan


            m[aid] = (z, v, rr, sex)
            global_ids.add(aid)


        if m:
            per_group_maps[(meas, sex)] = m


    if not per_group_maps:
        return ph


    # open outputs
    group_handles: Dict[Tuple[int, str], dict] = {}
    for (meas, sex), aid_map in per_group_maps.items():
        map_out = os.path.join(outdir, f"{meas}.{sex}.map")
        ped_out = os.path.join(outdir, f"{meas}.{sex}.ped")
        phe_out = os.path.join(outdir, f"{meas}.{sex}.pheno")
        map_df.to_csv(map_out, sep="\t", index=False, header=False)


        group_handles[(meas, sex)] = {
            "aid_map": aid_map,
            "ped_path": ped_out,
            "phe_path": phe_out,
            "ped_file": open(ped_out, "w", encoding="utf-8"),
            "phe_file": open(phe_out, "w", encoding="utf-8"),
            "wrote_any": False,
        }


    try:
        with open(ped_file, "r", encoding="utf-8", errors="replace") as fped:
            for raw in fped:
                if not raw.strip():
                    continue
                parts = raw.rstrip("\n").split()
                if len(parts) < 7:
                    continue


                V1, V2 = parts[0], parts[1]
                V1n = _norm_id(V1)
                if V1n not in global_ids:
                    continue


                for (meas, sex), info in group_handles.items():
                    aid_map = info["aid_map"]
                    if V1n not in aid_map:
                        continue
                    z, v, rz, sx = aid_map[V1n]


                    meta = parts[:6]
                    meta[4] = "2" if sx == "f" else "1"
                    # set PHE to rankz (Hao-style current util)
                    meta[5] = f"{rz}" if math.isfinite(rz) else "-9"


                    info["ped_file"].write(" ".join(meta + parts[6:]) + "\n")


                    info["phe_file"].write(
                        f"{V1} {V2} "
                        f"{(z if math.isfinite(z) else -9)} "
                        f"{(v if math.isfinite(v) else -9)} "
                        f"{(rz if math.isfinite(rz) else -9)}\n"
                    )
                    info["wrote_any"] = True
    finally:
        for info in group_handles.values():
            info["ped_file"].close()
            info["phe_file"].close()


    if not any(info["wrote_any"] for info in group_handles.values()):
        raise ValueError("[DO] wrote zero rows; no overlap between animal_id and DO PED V1.")


    return ph




# ------------------------------- WRAPPER ------------------------------- #
def generate_pheno_plink_fast(
    ped_file: str,
    map_file: str,
    pheno: pd.DataFrame,
    outdir: str,
    ncore: int = 1,
    *,
    panel_type: str = "NON_DO",
) -> pd.DataFrame:
    if pheno is None or pheno.empty:
        os.makedirs(outdir, exist_ok=True)
        return pd.DataFrame()


    pt = (panel_type or "NON_DO").upper()
    if pt == "DO":
        logging.info("[generate_pheno_plink_fast] using DO panel_type")
        return generate_pheno_plink_fast_do(ped_file, map_file, pheno, outdir)


    logging.info("[generate_pheno_plink_fast] panel_type=%r => NON-DO path", panel_type)
    return generate_pheno_plink_fast_non_do(ped_file, map_file, pheno, outdir)




# ----------------------------- Orchestrator ---------------------------- #
def fast_prepare_pylmm_inputs(
    ped_file: str,
    map_file: str,
    measure_id_directory: str,
    measure_ids: List,
    outdir: str,
    ncore: int,
    plink2_path: str,
    *,
    panel_type: str = "NON_DO",
    maf_threshold: Union[float, None] = None,
    reference_allele_path: Optional[str] = None,
    kinship_via_pylmm3: bool = True,
) -> None:
    os.makedirs(outdir, exist_ok=True)


    pheno = extract_pheno_measure(measure_id_directory, measure_ids)
    if pheno is None or pheno.empty:
        logging.info("[fast_prepare_pylmm_inputs] no phenotype rows extracted; nothing to do.")
        return


    used = generate_pheno_plink_fast(
        ped_file=ped_file,
        map_file=map_file,
        pheno=pheno,
        outdir=outdir,
        ncore=ncore,
        panel_type=panel_type,
    )
    if used is None or used.empty:
        logging.info("[fast_prepare_pylmm_inputs] no usable phenotypes after PED/MAP intersection; nothing to do.")
        return


    for measure_id in measure_ids:
        base_id = str(measure_id).split("_", 1)[0]
        for sex in ("f", "m"):
            ped_path = os.path.join(outdir, f"{base_id}.{sex}.ped")
            map_path = os.path.join(outdir, f"{base_id}.{sex}.map")
            pheno_path = os.path.join(outdir, f"{base_id}.{sex}.pheno")
            out_prefix = os.path.join(outdir, f"{base_id}.{sex}")


            if not (os.path.exists(ped_path) and os.path.exists(map_path) and os.path.exists(pheno_path)):
                continue


            # sample count is number of lines in pheno
            try:
                with open(pheno_path, "r", encoding="utf-8") as f_ph:
                    n_samples = sum(1 for _ in f_ph)
            except OSError:
                n_samples = 0


            if n_samples < MIN_SAMPLES_FOR_KINSHIP:
                logging.info(
                    "[fast_prepare_pylmm_inputs] skipping PLINK for %s.%s: n_samples=%d < %d",
                    base_id, sex, n_samples, MIN_SAMPLES_FOR_KINSHIP
                )
                continue


            generate_bed_bim_fam(
                plink2_path=plink2_path,
                ped_file=ped_path,
                map_file=map_path,
                output_prefix=out_prefix,
                relax_mind_threshold=False,
                maf_threshold=maf_threshold,
                sample_keep_path=None,
                autosomes_only=False,
                reference_allele_path=reference_allele_path,
            )


            if kinship_via_pylmm3:
                calculate_kinship_with_pylmm3(bfile_prefix=out_prefix)
            else:
                calculate_kinship_from_pedmap(
                    plink2_path=plink2_path,
                    pedmap_prefix=out_prefix,
                    kin_prefix=os.path.join(outdir, f"{base_id}.{sex}.kin"),
                )

