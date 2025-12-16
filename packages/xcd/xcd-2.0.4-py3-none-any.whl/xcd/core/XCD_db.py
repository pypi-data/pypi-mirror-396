import pandas as pd
from xcd.core import XCD_parsing

def db_available() -> bool:
    """Zatím vždy False, dokud nebude dostupné připojení."""
    try:
        import django 
        from django.conf import settings

        if settings.configured:
            return True
    except Exception:
        pass
        return False

def get_quant_data(case_id: str = None, path_csv=None) -> pd.DataFrame:
    """
    Vrátí kvantifikační data z DB nebo CSV.
    """
    if not db_available():
        return XCD_parsing.load_quant_any(path_csv)
    else:
        from xcd.django.models import Quantification, Sample
        qs = Quantification.objects.select_related("vzorek_id").values("vzorek_id__idf", "koncentrace", "koncentrace_y", "deg_a", "deg_y")
        # Později zde bude SELECT z DB
        return pd.DataFrame()

def get_sample_notes(case_id: str = None) -> dict:
    """
    Vrátí poznámky ke vzorkům z DB (zatím prázdné).
    """
    if not db_available():
        return {}
    else:
        from xcd.django.models import Sample
        samples = Sample.objects.values("idf", "poznamka")

        return {s["idf"]:s["poznamka"] for s in samples if s["poznamka"]}


# ------------------------------
# DJANGO – načtení doplňkových dat z PostgreSQL
# ------------------------------

def load_db_data_for_samples(sample_names):
    try:
        from xcd.django.models import Sample, Quantification
    except Exception:
        return {}

    if not sample_names:
        return {}

    # načti vzorky dle IDF
    qs = Sample.objects.filter(idf__in=sample_names).values("id", "idf", "poznamka")
    rows = list(qs)

    # mapování id -> idf a poznámky
    id_to_idf = {r["id"]: r["idf"] for r in rows}
    notes_dict = {r["idf"]: (r.get("poznamka") or "") for r in rows}

    # kvantifikace pro tyto id
    q = Quantification.objects.filter(vzorek_id__in=id_to_idf.keys()) \
        .values("vzorek_id", "koncentrace", "koncentrace_y", "deg_a", "deg_y")

    import pandas as pd
    quant_df = pd.DataFrame(list(q))

    if quant_df.empty:
        return {"quant_df": pd.DataFrame(columns=["Sample","A","Y","DI_A","DI_Y"]),
                "notes_dict": notes_dict}

    # napojení přes mapování
    quant_df["Sample"] = quant_df["vzorek_id"].map(id_to_idf)
    quant_df = quant_df.rename(columns={
        "koncentrace":"A", "koncentrace_y":"Y", "deg_a":"DI_A", "deg_y":"DI_Y",
    }).drop(columns=["vzorek_id"], errors="ignore") \
     .reindex(columns=["Sample","A","Y","DI_A","DI_Y"])

    return {"quant_df": quant_df, "notes_dict": notes_dict}