import pandas as pd
import csv
import os
from xcd.core import XCD_utils, XCD_kits

# ----------------------
# Načtení kvantifikace CSV
# ----------------------

def load_quant_any(paths):
    """
    Načte kvantifikační soubory různých formátů (CSV, XLS/XLSX, TXT).
    Výstupní DataFrame má sjednocené sloupce:
        Sample | Human | Male | DI_A | DI_Y | A/Y
    """

    if not paths:
        return pd.DataFrame()
    if isinstance(paths, str):
        paths = [paths]

    results = []

    for path in paths:
        ext = os.path.splitext(path)[1].lower()

        try:
            # -------------------------
            # 1) Excel/XLSX (řádkový formát s "Target Name")
            # -------------------------
            if ext in [".xls", ".xlsx"]:
                df = pd.read_excel(path)

                if "Sample Name" in df.columns and "Target Name" in df.columns:
                    grouped = df.groupby("Sample Name")
                    for sample, g in grouped:
                        sample = str(sample).strip().upper()
                        human = male = None
                        human_deg = male_deg = None

                        for _, row in g.iterrows():
                            t = str(row["Target Name"]).strip().lower()
                            q = row.get("Quantity Mean", row.get("Quantity"))
                            if pd.isna(q):
                                continue
                            try:
                                q = float(q)
                            except:
                                q = None

                            if t == "human":
                                human = q
                            elif t == "male":
                                male = q
                            elif "degrad" in t:
                                human_deg = q

                        di_a = (human / human_deg) if human and human_deg else None
                        di_y = (male / male_deg) if male and male_deg else None
                        ratio = (human / male) if human and male and male != 0 else None

                        results.append({
                            "Sample": sample,
                            "A": round(human, 4) if human else None,
                            "Y": round(male, 4) if male else None,
                            "DI_A": round(di_a, 2) if di_a else None,
                            "DI_Y": round(di_y, 2) if di_y else None,
                            "A/Y": round(ratio, 2) if ratio else None,
                        })

            # -------------------------
            # 2) TXT (MC_data style: Small Auto, Y, Degradation Index)
            # -------------------------
            elif ext == ".txt":
                with open(path, encoding="utf-8", errors="ignore") as f:
                    lines = [l.strip().split("\t") for l in f if l.strip()]
                header = lines[0]
                rows = lines[1:]

                # Najdeme indexy
                idx_sample = header.index("Sample Name") if "Sample Name" in header else None
                idx_target = header.index("Target Name") if "Target Name" in header else None
                idx_quantity = header.index("Quantity") if "Quantity" in header else None
                idx_di = header.index("Degradation Index") if "Degradation Index" in header else None

                data = {}
                for row in rows:
                    if idx_sample is None or idx_target is None:
                        continue
                    sample = row[idx_sample].strip().upper()
                    target = row[idx_target].strip().lower()
                    q = None
                    if idx_quantity is not None and idx_quantity < len(row):
                        try:
                            q = float(row[idx_quantity])
                        except:
                            q = None

                    if sample not in data:
                        data[sample] = {"Human": None, "Male": None, "DI_A": None, "DI_Y": None, "A/Y": None}

                    if "small auto" in target:
                        data[sample]["Human"] = q
                    elif target == "y":
                        data[sample]["Male"] = q
                    elif "degradation index" in target:
                        data[sample]["DI_A"] = q

                for sample, vals in data.items():
                    human = vals["Human"]
                    male = vals["Male"]
                    di_a = vals["DI_A"]
                    ratio = (human / male) if human and male and male != 0 else None
                    results.append({
                        "Sample": sample,
                        "A": round(human, 4) if human else None,
                        "Y": round(male, 4) if male else None,
                        "DI_A": round(di_a, 2) if di_a else None,
                        "DI_Y": None,
                        "A/Y": round(ratio, 2) if ratio else None,
                    })

            # -------------------------
            # 3) CSV (starý formát s TestSample)
            # -------------------------
            else:
                with open(path, encoding="utf-8", errors="ignore") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if not row or len(row) < 3:
                            continue
                        if "TestSample" in row:
                            sample_id = row[1].strip().upper()
                            male = human = male_deg = human_deg = None

                            # projdeme řádek a hledáme štítky
                            for i, lab in enumerate(row):
                                if lab == "Male":
                                    try:
                                        male = None if row[i+5].strip() == "--" else float(row[i+5])
                                    except:
                                        pass
                                elif lab == "Human":
                                    try:
                                        human = None if row[i+5].strip() == "--" else float(row[i+5])
                                    except:
                                        pass
                                elif "Male Degradation" in lab:
                                    try:
                                        male_deg = None if row[i+5].strip() == "--" else float(row[i+5])
                                    except:
                                        pass
                                elif "Human Degradation" in lab:
                                    try:
                                        human_deg = None if row[i+5].strip() == "--" else float(row[i+5])
                                    except:
                                        pass

                            # výpočty
                            di_a = (human / human_deg) if human and human_deg else None
                            di_y = (male / male_deg) if male and male_deg else None
                            ratio = (human / male) if male and human and male != 0 else None

                            results.append({
                                "Sample": sample_id,
                                "A": round(human, 4) if human else None,
                                "Y": round(male, 4) if male else None,
                                "DI_A": round(di_a, 2) if di_a else None,
                                "DI_Y": round(di_y, 2) if di_y else None,
                                "A/Y": round(ratio, 2) if ratio else None,
                            
                            })



        except Exception as e:
            print(f"⚠️ Nepodařilo se načíst {path}: {e}")

    return pd.DataFrame(results)


# =========================================================
# 🧩 1️⃣ Funkce build_results_df — hlavní logika zpracování jednoho runu
# =========================================================
def build_results_df(df_or_path, kit_name: str = None, pattern: str = None):
    """
    Zpracuje JEDEN run (soupisku) z GeneMapper TXT.
    - Načte TXT nebo DataFrame
    - Detekuje ladder a vytvoří ladder_dict jen pro tento run (NEignorujeme)
    - Vyhodnotí vzorky (PC/NC/LADDER jsou vyřazeny z výsledků)
    - Vrací results, header, df, log_list, normalized_kit
    """
    log_list = []

    # --- Bezpečné načtení DataFrame ---
    if isinstance(df_or_path, str):
        if not os.path.exists(df_or_path):
            raise FileNotFoundError(f"Soubor nenalezen: {df_or_path}")
        try:
            df = pd.read_csv(df_or_path, sep="\t")
        except Exception as e:
            raise ValueError(f"Chyba při čtení TXT souboru: {e}")
    elif isinstance(df_or_path, pd.DataFrame):
        df = df_or_path
    else:
        raise TypeError(f"Neplatný vstup typu: {type(df_or_path)} — očekávám cestu nebo DataFrame")

    # --- Základní informace o runu ---
    if "Run Name" in df.columns and not df["Run Name"].dropna().empty:
        run_name = str(df["Run Name"].dropna().iloc[0]).strip()
    else:
        run_name = "Run ?"

    run_date = ""
    if "Run Date" in df.columns and not df["Run Date"].dropna().empty:
        run_date = str(df["Run Date"].dropna().iloc[0]).strip()

    # --- Kit: autodetekce + možnost přepsat ručně z argumentu ---
    if "Panel" in df.columns and not df["Panel"].dropna().empty:
        raw_kit = str(df["Panel"].dropna().iloc[0]).strip()
    else:
        raw_kit = "Neznámý"

    try:
        normalized_kit = XCD_kits.normalize_kit_name(raw_kit)
    except Exception:
        normalized_kit = raw_kit

    sample_meta = {}

    if kit_name:  # uživatel přepsal autodetekci
        try:
            normalized_kit = XCD_kits.normalize_kit_name(kit_name)
        except Exception:
            normalized_kit = kit_name

    run_header = f"Soupiska: {run_name}   Odečet: {run_date}"

    # --- Ladder pro aktuální run (používáme pro OL/velikosti, ale nevracíme mezi vzorky) ---
    ladder = df[df["Sample Name"] == "LADDER"].copy()
    ladder_dict = {}

    def _to_float_or_none(x):
        try:
            return float(str(x).replace(",", "."))
        except Exception:
            return None

    if not ladder.empty and "Marker" in ladder.columns:
        for marker in ladder["Marker"].unique():
            subset = ladder[ladder["Marker"] == marker]
            pairs = []
            for _, r in subset.iterrows():
                for i in range(1, 41):
                    a = r.get(f"Allele {i}")
                    s = r.get(f"Size {i}")
                    if pd.isna(a) or pd.isna(s):
                        continue
                    a_str = str(a).strip()
                    s_val = _to_float_or_none(s)
                    if s_val is None:
                        continue
                    a_val = _to_float_or_none(a_str)
                    pairs.append((a_str, s_val, a_val))
            pairs.sort(key=lambda t: t[1])  # seřazeno podle velikosti
            ladder_dict[marker] = pairs

    # --- Vzorky do reportu (PC/NC/LADDER ven) ---
    samples = df[~df["Sample Name"].isin(["LADDER", "PC", "NC"])].copy()
    results = {}

    # --- Zpracování řádek se signály ---
    for _, row in samples.iterrows():
        marker = row.get("Marker")
        if pd.isna(marker):
            continue
        sample = str(row.get("Sample Name", "")).strip()
        if not sample:
            continue
        
        if sample not in sample_meta:
            sample_meta[sample] = {"run:": run_name, "kit": normalized_kit}

        dye = row.get("Dye", None)
        ladder_sizes = ladder_dict.get(marker, [])

        alleles = []
        locus_alleles = []
        all_sample_alleles = []

        # výšky v lokusu (kvůli heuristikám)
        heights_in_locus = []
        for j in range(1, 41):
            h_raw = row.get(f"Height {j}", 0)
            try:
                h_val = float(h_raw)
                if h_val:
                    heights_in_locus.append(h_val)
            except Exception:
                pass

        # projdi všechny možné alely v řádku
        for i in range(1, 41):
            allele = row.get(f"Allele {i}")
            height = row.get(f"Height {i}")
            size = row.get(f"Size {i}")
            area = row.get(f"Peak Area {i}")

            all_sample_alleles.append((size, dye, allele, height, marker))

            valid = XCD_utils.validate_allele(
                allele, height, size, area,
                ladder_sizes=ladder_sizes,
                sample=sample,
                run=run_name,
                kit=normalized_kit,
                locus=marker,
                dye=dye,
                log_list=log_list,
                is_fu=XCD_utils.is_fu_sample(sample),
                locus_alleles=locus_alleles,
                all_sample_alleles=all_sample_alleles,
                locus_all_heights=heights_in_locus,
            )

            if valid:
                alleles.append((valid, height))
                locus_alleles.append((valid, height))

        # 1–2 nejvyšší pro srovnávací, vše pro FU
        if alleles and not XCD_utils.is_fu_sample(sample):
            alleles = XCD_utils.top2_alleles(alleles)

        case_id = XCD_utils.get_case_prefix(sample, pattern)
        results.setdefault(case_id, {}).setdefault(sample, {}).setdefault(marker, ([], dye))
        old_alleles, old_dye = results[case_id][sample][marker]
        results[case_id][sample][marker] = (old_alleles + alleles, dye or old_dye)

    # --- Sloučení kontrol: QS1/QS2 a IQCS/IQCL ---
    for case_id, smap in results.items():
        for sample, loci in smap.items():
            if "QS1" in loci or "QS2" in loci:
                q1 = loci.pop("QS1", ([], None))
                q2 = loci.pop("QS2", ([], None))
                loci["QS1|QS2"] = (q1[0] + q2[0], q1[1] or q2[1])

            if "IQCS" in loci or "IQCL" in loci:
                i1 = loci.pop("IQCS", ([], None))
                i2 = loci.pop("IQCL", ([], None))
                loci["IQCS|IQCL"] = (i1[0] + i2[0], i1[1] or i2[1])

    return results, run_header, df, log_list, normalized_kit

# ----------------------
# Načtení TXT → results
# ----------------------
def build_results(path_txt: str, kit_name: str = None):
    """
    Načte GeneMapper TXT a vrátí:
      - results (dict)
      - run_header (str)
      - původní DataFrame
      - log_list (list of dict)
      - raw_kit (detekovaný kit z GeneMapperu)
    """
    df = pd.read_csv(path_txt, sep="\t")
    return build_results_df(df, kit_name)

# =========================================================
# 🧩 3️⃣ build_all_results – pro více runů v jednom TXT
# =========================================================
def build_all_results(path_txt: str, selected_kit=None):
    """
    Načte TXT se všemi runy (soupiskami).
    Vrací:
      - results_all     : dict[case_id][sample] -> ...
      - run_headers     : dict[run_name] -> "Soupiska: ... Odečet: ..."
      - df              : původní DataFrame
      - logs_all        : list log záznamů
      - kits_all        : dict[run_name] -> normalized_kit
      - sample_meta_all : dict[sample] -> {"run": run_name, "kit": normalized_kit}
    """
    df = pd.read_csv(path_txt, sep="\t")
    if "Run Name" not in df.columns:
        raise ValueError("Chybí sloupec 'Run Name' v TXT souboru.")

    runs = (
        df.dropna(subset=["Run Name"])
          .loc[:, ["Run Name", "Panel"]]
          .drop_duplicates()
    )

    results_all, logs_all = {}, []
    run_headers, kits_all = {}, {}
    sample_meta_all = {}  # <<<<<<<<<< DŮLEŽITÉ

    for _, run_row in runs.iterrows():
        run_name = str(run_row["Run Name"]).strip()
        raw_kit  = str(run_row["Panel"]).strip() if "Panel" in run_row else "Neznámý"

        # uživatelské přepsání kitu (volitelné)
        kit_to_use = selected_kit or raw_kit

        sub_df = df[df["Run Name"] == run_name].copy()

        # build_results_df vrací: results, run_header, df_sub, log_list, normalized_kit
        results, run_header, _df_sub, log_list, normalized_kit = build_results_df(
            sub_df, kit_name=kit_to_use
        )

        run_headers[run_name] = run_header
        kits_all[run_name]    = normalized_kit

        # >>> ZDE naplníme sample_meta_all <<<
        for _case_id, smap in results.items():
            for sample in smap.keys():
                # poslední výhra – ale v rámci jednoho TXT je to stabilní
                sample_meta_all[sample] = {"run": run_name, "kit": normalized_kit}

        # sloučení výsledků a logů
        for case_id, smap in results.items():
            results_all.setdefault(case_id, {}).update(smap)
        logs_all.extend(log_list)

    return results_all, run_headers, df, logs_all, kits_all, sample_meta_all


def parse_txt_for_options(path_txt: str):
    """Z TXT načti seznam případů a znalců pro comboboxy v GUI."""
    if not path_txt or not os.path.exists(path_txt):
        return set(), set()
    df = pd.read_csv(path_txt, sep="\t")
    samples = df[~df["Sample Name"].isin(["LADDER", "PC", "NC"])]
    case_ids = set()
    experts = set()
    for s in samples["Sample Name"].unique():
        case_ids.add(XCD_utils.get_case_id(s))
        code = s[:2] if len(s) >= 2 and s[:2].isalpha() else ""
        if code:
            experts.add(code)
    return case_ids, experts