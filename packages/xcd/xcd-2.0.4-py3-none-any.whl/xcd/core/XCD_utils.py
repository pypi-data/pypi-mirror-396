from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from xcd.core.XCD_kits import KITS
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import  Paragraph
import pandas as pd
import re
import math
# ----------------------
# Font (Calibri Light → fallback Helvetica)
# ----------------------
try:
    pdfmetrics.registerFont(TTFont("CalibriLight", "calibril.ttf"))
    pdfmetrics.registerFont(TTFont("Calibri", "calibri.ttf"))
    pdfmetrics.registerFont(TTFont("CalibriItalic", "calibrii.ttf"))
    pdfmetrics.registerFont(TTFont("CalibriLightItalic", "calibrili.ttf"))
    DEFAULT_FONT = "CalibriLight"
except Exception:
    DEFAULT_FONT = "Helvetica"

# ----------------------
# Parametry
# ----------------------
HEIGHT_THRESHOLD = 50
SIZE_TOLERANCE = 0.5
FONT_MIN, FONT_MAX = 5.0, 16.0
ROW_HEIGHT_MARKER = 24   # markerové řádky
ROW_HEIGHT_QUANT = 16    # kvantifikační řádky
COL_WIDTHS = [60] + [120, 120, 120, 120]

# Barvy lokusů (Y → black pro čitelnost)
DYE_COLORS = {
    "B": colors.blue,
    "G": colors.green,
    "Y": colors.black,   # žlutý kanál tiskneme černě
    "R": colors.red,
    "P": colors.purple
}

def format_locus_for_log(locus: str, dye: str) -> Paragraph:
    """Vrátí Paragraph pro lokus v logu, barevně podle dye."""
    style = ParagraphStyle(
        name="LogLocus",
        fontName="Calibri",
        fontSize=9,
        textColor=DYE_COLORS.get(str(dye), colors.black),
        alignment=0
    )
    return Paragraph(locus, style)

def merged_kit_order(kit_name: str):
    """Vrátí pořadí lokusů dle zvoleného kitu; QS1 a QS2 sloučí na QS1|QS2, pokud existují."""
    base = KITS[kit_name]
    out = []
    skip = set()
    for loc in base:
        if loc in skip:
            continue
        if loc == "QS1":
            out.append("QS1|QS2")
            skip.add("QS2")
        elif loc == "QS2":
            if "QS1|QS2" not in out:
                out.append("QS1|QS2")

        elif loc == "IQCS":
            out.append("IQCS|IQCL")
            skip.add("IQCL")
        elif loc == "IQCL":
            if "IQCS|IQCL" not in out:
                out.append("IQCS|IQCL")

        else:
            out.append(loc)
    return out

# ----------------------
# Pomocné funkce
# ----------------------
def font_size_from_height(height, local_max):
    if not height or height <= 0 or not local_max:
        return FONT_MIN
    if height <= 50:
        return FONT_MIN
    scale = (height - 50) / (local_max - 50) if local_max > 50 else 1
    scale = max(0, min(scale, 1))
    size = FONT_MIN + (FONT_MAX - FONT_MIN) * scale
    return round(size * 2) / 2



def format_alleles_for_cell(
    alleles, local_max, is_fu, highlight_major=False,
    cell_width=120, bold_indices=None, safe_width=90
):
    if not alleles:
        return ""

    if bold_indices is None:
        bold_indices = []

    # velikosti fontů (RFU škálování u FU, jinak 16)
    font_sizes = []
    for allele, height in alleles:
        fsize = font_size_from_height(height, local_max) if is_fu else 16
        font_sizes.append(fsize)

    # odhad šířky textu
    est_width = 0
    for (allele, _), fs in zip(alleles, font_sizes):
        est_width += pdfmetrics.stringWidth(str(allele), DEFAULT_FONT, fs)
    if len(alleles) > 1:
        est_width += pdfmetrics.stringWidth("|", DEFAULT_FONT, min(font_sizes)) * (len(alleles) - 1)

    # proporční zmenšení pokud překročí safe_width
    if est_width > safe_width:
        scale = safe_width / est_width
        font_sizes = [max(5, fs * scale) for fs in font_sizes]
        #print(f"[DEBUG] SAFE shrink: {len(alleles)} alel, est_width={est_width:.1f}, scale={scale:.2f}")

    # extra kontrola – pokud i po zmenšení máme moc velké fonty → snížit o 1 bod
    # to zabrání zalomení
    max_font = max(font_sizes)
    if max_font > 10:  # třeba cokoliv nad 10 riskuje zalomení
        font_sizes = [fs - 1 for fs in font_sizes]
        #print(f"[DEBUG] Extra shrink: {len(alleles)} alel, max_font={max_font}")

    ZWSP = "\u200b"

    # složení textu
    parts = []
    for idx, ((allele, height), fs) in enumerate(zip(alleles, font_sizes)):
        if highlight_major and idx in bold_indices:
            parts.append(f'<font name="Calibri" size={fs}>{allele}</font>')
        else:
            parts.append(f'<font name="CalibriLight" size={fs}>{allele}</font>')
        if idx < len(alleles) - 1:
            parts.append(f"|{ZWSP}")

    text = "".join(parts)
    style = ParagraphStyle(
        name="Alela",
        fontName=DEFAULT_FONT,
        fontSize=10,
        leading=max(font_sizes) + 4,  # už nikdy nezvětšujeme řádek dvojnásobně
        textColor=colors.black,
        alignment=0,
        spaceBefore=0,
        spaceAfter=0,
        wordWrap='LTR',
        splitLongWords=0,
    )
    return Paragraph(text, style)



def sort_alleles_numeric(alleles):
    """
    Seřadí alely číselně podle jejich hodnoty (pokud to jde).
    """
    def parse_val(a):
        try:
            return float(a[0])  # hodnota alely jako číslo
        except Exception:
            return a[0]         # fallback na text (např. 'OL')
    return sorted(alleles, key=parse_val)

HEIGHT_THRESHOLD = 50
SIZE_TOLERANCE = 0.5  # tolerance ve velikosti (bp) pro porovnání s ladderem

# ----------------------
# Povolené mikrovarianty dle motivu
# ----------------------

# default = 4 (tetramer); u známých pentamerů nastavíme 5
PENTAMER_LOCUS_HINTS = {"Penta D", "Penta E"}
# můžeš libovolně rozšířit; SE33 je tetranukleotid (necháme 4)
# Y-lokusy obvykle 4; pokud víš o jiných, doplň sem.

def get_motif_length(locus: str) -> int:
    if locus in PENTAMER_LOCUS_HINTS:
        return 5
    return 4  # default

def max_micro_decimal(motif_len: int) -> float:
    # pro tetramer .1-.3, pro pentamer .1-.4, pro trimer .1-.2, atd.
    return (motif_len - 1) / 10.0  # 4→0.3, 5→0.4

# ----------------------
# Pomocné funkce pro OL
# ----------------------

def transform_ol_with_ladder(meas_size: float,
                             ladder_ref: list,
                             size_tol: float,
                             locus: str) -> str | None:
    """
    Převod OL → alelová hodnota (např. 10.1, 10.2…).
    - Najde sousední celé repeat alely
    - Pokud chybí horní/dolní soused, dopočítá jej z typického sklonu
    - Vrátí základ + .mikrovarianta, pokud spadá do povoleného rozsahu
    """

    # --- Základní kontrola ---
    if meas_size is None or not ladder_ref:
        #print(f"[OL→allele] {locus}: ❌ ladder_ref prázdný nebo meas_size=None")
        return None

    motif = get_motif_length(locus)
    max_frac = max_micro_decimal(motif)

    # --- Připrav integer body z ladderu ---
    int_pts = [(float(a), float(s)) for (a, s, a_num) in ladder_ref
               if a_num is not None and float(a_num).is_integer()]
    if len(int_pts) < 1:
        #print(f"[OL→allele] {locus}: ❌ žádné celé repeat body v ladderu")
        return None
    int_pts.sort(key=lambda x: x[1])

    # --- typický sklon v bp/repeat ---
    if len(int_pts) >= 2:
        diffs = [int_pts[i+1][1] - int_pts[i][1] for i in range(len(int_pts)-1)]
        diffs = [d for d in diffs if d > 0]
        bp_per_repeat = sum(diffs) / len(diffs)
    else:
        bp_per_repeat = 4.0  # nouzová defaultní hodnota

    below = None
    above = None

    # --- hledej přirozené sousedy ---
    for i in range(len(int_pts) - 1):
        s1 = int_pts[i][1]
        s2 = int_pts[i + 1][1]
        if s1 <= meas_size <= s2:
            below = int_pts[i]
            above = int_pts[i + 1]
            break

    # --- extrapolace ---
    if below is None and meas_size > int_pts[-1][1]:
        below = int_pts[-1]
        above = (below[0] + 1, below[1] + bp_per_repeat)
    if above is None and meas_size < int_pts[0][1]:
        above = int_pts[0]
        below = (above[0] - 1, above[1] - bp_per_repeat)

    # --- pokud pořád nic ---
    if below is None or above is None:
        #print(f"[OL→allele] {locus}: ❌ žádní sousedé pro {meas_size:.2f} bp")
        return None

    # --- výpočty ---
    a_below, s_below = below
    a_above, s_above = above
    slope_bp_per_repeat = (s_above - s_below) / (a_above - a_below)
    bp_per_nt = slope_bp_per_repeat / motif
    offset_bp = meas_size - s_below
    extra_nt = round(offset_bp / bp_per_nt)

    expected_bp = s_below + extra_nt * bp_per_nt
    diff_bp = meas_size - expected_bp

    # --- výpis všech parametrů ---
    #print(f"[OL→allele] {locus}: size={meas_size:.2f} bp | "
    #      f"below={a_below}@{s_below:.2f} | above={a_above}@{s_above:.2f} | "
    #     f"motif={motif} | Δbp/repeat={slope_bp_per_repeat:.2f} | "
    #      f"bp/nt={bp_per_nt:.3f} | offset={offset_bp:.2f} bp "
    #      f"→ extra_nt={extra_nt} | diff={diff_bp:.3f} bp")

    # --- kontrola rozsahu mikrovarianty ---
    if extra_nt <= 0 or extra_nt > motif - 1:
        #print(f"[OL→allele] {locus}: ❌ mimo rozsah mikrovarianty ({extra_nt})")
        return None

    allele_val = f"{int(a_below)}.{extra_nt}"

    # --- ověření tolerance ---
    if abs(diff_bp) <= size_tol:
        #print(f"[OL→allele] {locus}: ✅ transformováno na {allele_val} "
        #      f"(|Δ|={abs(diff_bp):.3f} ≤ {size_tol})")
        return allele_val
    else:
        #print(f"[OL→allele] {locus}: ❌ zamítnuto (|Δ|={abs(diff_bp):.3f} > {size_tol})")
        return None



# ----------------------
# Artefakty
# ----------------------

def detect_artifact(allele, height, size,
                    locus_alleles, dye, all_sample_alleles, locus_name=None):
    """
    Vrací důvod artefaktu, nebo None.
    - locus_alleles: [(allele, height)] pro kontrolu stutteru
    - all_sample_alleles: [(size, dye, allele, height)] pro pull-up (jen v rámci vzorku)
    """
    if height < HEIGHT_THRESHOLD:
        return "artefakt (pod prahem RFU)"

    # stutter (±1 repeat od silnější alely v lokusu a RFU výrazně nižší)
    for main_allele, main_height in locus_alleles:
        try:
            a_val = float(allele)
            m_val = float(main_allele)
            if abs(a_val - m_val) == 1 and height < 0.03 * (main_height or 1):
                return f"stutter alely {main_allele}"
        except Exception:
            continue

    # pull-up (stejná size jako jiný peak, ale jiný dye, v tomtéž vzorku)

    for s, d, a, h, _ in all_sample_alleles:
        try:
            if abs(size - s) <= SIZE_TOLERANCE and dye != d:
                # Definuj barvy pro PDF
                dye_colors_html = {
                    "B": "#0070C0",    # Blue
                    "G": "#00B050",    # Green
                    "Y": "#FFD700",    # Yellow
                    "R": "#FF0000",    # Red
                    "P": "#7030A0",    # Purple
                }
                color_html = dye_colors_html.get(d, "#000000")

                # Poznámka pro log s barvou lokusu
                return (
                    f"pull-up z alely <b>{a}</b> "
                    f"(<font color='{color_html}'>{locus_name or '?'} ({d}))</font>"
                )
        except Exception:
            continue

    return None

def _is_nan(x):
    return isinstance(x, float) and math.isnan(x)

def safe_str(x):
    if x is None or _is_nan(x):
        return ""
    return str(x)
def safe_join(sep, items):
    return sep.join(safe_str(i) for i in items if i is not None and not _is_nan(i))

def detect_cluster_artifact(locus_peaks, log_list, sample, locus, dye):
    """
    Detekuje clustery – skupiny ≥3 slabých píků (<10 % maxima lokusu)
    s podobnou výškou (≤2.5× rozdíl) a vzdáleností sousedních <2 bp.
    Vrací seznam alel (bez OL), které patří do clusteru.
    """
    if not locus_peaks or len(locus_peaks) < 3:
        return []

    # validní píky s výškou
    valid_peaks = [(a, s, h) for a, s, h in locus_peaks if h and h > 0]
    if len(valid_peaks) < 3:
        return []

    # maximum lokusu
    max_height = max(h for _, _, h in valid_peaks)

    # jen slabé píky (≤10 % maxima)
    low_peaks = [(a, s, h) for a, s, h in valid_peaks if h <= 0.10 * max_height]
    if len(low_peaks) < 3:
        return []

    # seřaď podle velikosti
    low_peaks.sort(key=lambda x: x[1])

    clusters = []
    current_cluster = [low_peaks[0]]

    MAX_GAP_BP = 2.0        # mezera mezi sousedními píkami
    HEIGHT_RATIO_TOL = 2.5  # max. poměr výšek v rámci clusteru

    # --- seskupování podle blízkosti ---
    for i in range(1, len(low_peaks)):
        prev = low_peaks[i - 1]
        curr = low_peaks[i]
        if curr[1] - prev[1] <= MAX_GAP_BP:
            current_cluster.append(curr)
        else:
            if len(current_cluster) >= 3:
                clusters.append(current_cluster)
            current_cluster = [curr]
    if len(current_cluster) >= 3:
        clusters.append(current_cluster)

    clustered_alleles = set()

    # --- kontrola výšek v každém clusteru ---
    for group in clusters:
        heights = [h for _, _, h in group]
        if max(heights) / min(heights) <= HEIGHT_RATIO_TOL:
            # ignoruj clustery tvořené výhradně OL
            numeric_group = [a for a, _, _ in group if safe_str(a) and not safe_str(a).upper().startswith("OL")]
            if not numeric_group:
                continue

            # přidej do seznamu odstraněných
            clustered_alleles.update(numeric_group)

            # loguj jen jednou pro tento lokus (žádné duplikáty)
            if log_list is not None:
                already_logged = {
                    (entry["Sample"], entry["Locus"], entry["Allele"])
                    for entry in log_list
                }
                allele_str = safe_join(" - ", numeric_group)
                key = (sample, locus, allele_str)
                if key not in already_logged:
                    log_list.append({
                        "Sample": sample,
                        "Locus": locus,
                        "Allele": allele_str,
                        "Reason": "cluster artefakt",
                        "Dye": dye,
                    })

    return list(clustered_alleles)



# ----------------------
# Validate allele
# ----------------------

def validate_allele(allele, height, size, area,
                    ladder_sizes,
                    sample=None, case_id=None, run=None, kit=None,
                    locus=None, dye=None,
                    log_list=None, is_fu=False,
                    locus_alleles=None,
                    all_sample_alleles=None,
                    locus_all_heights=None):

    if pd.isna(allele) or pd.isna(height) or pd.isna(size):
        return None

    # --- CLUSTER ARTIFACT DETECTION ---

    locus_peaks = []
    if all_sample_alleles:
            for s, d, a, h, loc in all_sample_alleles:
                if loc == locus:
                    locus_peaks.append((a, s, h))
    
    if not any (a ==allele for a, _, _ in locus_peaks):
        locus_peaks.append((allele, size, height))

    clustered = detect_cluster_artifact(locus_peaks, log_list, sample, locus, dye)
    if allele in clustered:
        return None

    if str(allele).upper() == "OL":

        # --- Spočítej maximum z výšek všech alel v aktuálním lokusu ---
        heights_in_locus = locus_all_heights or []
        max_height = max(heights_in_locus) if heights_in_locus else 0

        # dynamický práh (10 % maxima, min. 100 RFU)
        dynamic_threshold = max(100, max_height * 0.10)
        # bezpečně převeď výšku aktuální OL
        try:
            h_val = float(height) if height is not None else 0
        except Exception:
            h_val = 0

        # --- Filtr: OL pod 10 % maxima se rovnou vyřadí ---
        if h_val < dynamic_threshold:
            # (nechceme logovat, jen odstranit)
            return None

        # --- Kontrola poměru plocha/výška (geometrický filtr) ---
        try:
            if not area or float(area) / h_val < 7 or float(area) / h_val > 15:
                return None
        except Exception:
            return None

        # --- Transformace OL podle ladderu ---
        new_label = transform_ol_with_ladder(size, ladder_sizes, SIZE_TOLERANCE, locus or "")

        if new_label:
            # Pokud je směsný vzorek (FU), zapíšeme transformaci do logu
            if log_list is not None:
                log_list.append({
                    "Sample": sample,
                    "Locus": locus,
                    "Allele": "OL",
                    "Reason": f"-> {new_label}",
                    "Dye": dye,
                })
            return new_label

        # pokud se OL nepodaří transformovat, odstraníme ji
        return None


    # --- kontrola morfologie jen pro reálné alely ---
    if height and area:
        ratio = area / height
        if ratio < 7 or ratio > 15:
            if is_fu and log_list is not None:
                log_list.append({
                    "Sample": sample,
                    "Locus": locus, "Allele": allele,
                    "Reason": f"špatná morfologie peaku", 
                    "Dye": dye,
                })
            return None

    # --- artefakty (pod RFU, stutter, pull-up) ---
    reason = detect_artifact(
        allele, height, size,
        locus_alleles=locus_alleles or [],
        dye=dye,
        all_sample_alleles=all_sample_alleles or [],
        locus_name=locus,
    )

    if reason:
        if is_fu and log_list is not None:
            log_list.append({
                "Sample": sample,
                "Locus": locus, "Allele": allele,
                "Reason": f"{reason}", 
                "Dye": dye,
            })
        return None

    # --- validní alela ---
    return normalize_allele_str(allele)

def select_alleles(alleles, is_fu):
    """
    Vrátí seznam alel podle typu vzorku:
    - FU (směsný profil) → všechny alely, seřazené číselně.
    - ne-FU (srovnávací vzorek) → 2 nejsilnější podle height,
      potom seřazené číselně.
    """
    if is_fu:
        return sort_alleles_numeric(alleles)
    else:
        # vyber top2 podle RFU
        top2 = sorted(alleles, key=lambda x: x[1] or 0, reverse=True)[:2]
        # seřaď top2 číselně
        return sort_alleles_numeric(top2)


def parse_sample_name(sample: str, pattern: str):
    """
    Rozkóduje název vzorku podle patternu (např. 'iiyydCCCCdssnn').
    Malá písmena = přesný počet znaků
    Velká písmena = proměnlivá délka (1+)
    """

    sample = sample.strip()

    # mapování symbolů
    mapping = {
        "i": r"[A-Z]",
        "I": r"[A-Z]+",
        "y": r"\d",
        "Y": r"\d+",
        "c": r"\d",
        "C": r"\d+",
        "s": r"[A-Z]",
        "S": r"[A-Z]+",
        "n": r"\d",
        "N": r"\d+",
        "d": r"[-_]",
    }

    regex = "".join(mapping.get(ch, ch) for ch in pattern)
    match = re.match(regex, sample)
    if not match:
        return None

    # extrakce konkrétních částí podle pořadí
    parts = {"id": "", "year": "", "case": "", "type": "", "num": ""}
    for ch, val in zip(pattern, sample):
        if ch.lower() == "i":
            parts["id"] += val
        elif ch.lower() == "y":
            parts["year"] += val
        elif ch.lower() == "c":
            parts["case"] += val
        elif ch.lower() == "s":
            parts["type"] += val
        elif ch.lower() == "n":
            parts["num"] += val
    return parts



def get_case_id(sample_name: str, pattern: str = None):
    if not sample_name:
        return ""
    if pattern:
        parsed = parse_sample_name(sample_name, pattern)
        if parsed and parsed["case"] and parsed["year"]:
            return f"{int(parsed['case'])}/{parsed['year']}"
        elif parsed and parsed["case"]:
            return str(int(parsed["case"]))
    # fallback – původní metoda
    parts = str(sample_name).split("-")
    return "-".join(parts[:2]) if len(parts) >= 2 else sample_name


def get_case_prefix(sample_name: str, pattern: str = None):
    
    sample_name = sample_name.strip().upper()
    if "-" in sample_name:
        parts = sample_name.split("-")
        if len(parts)>= 3:
            return "-".join(parts[:2])
        elif len(parts) == 2:
            return parts[0]
    return sample_name

def get_expert_code(sample_name: str, pattern: str = None):
    if not sample_name:
        return ""
    if pattern:
        parsed = parse_sample_name(sample_name, pattern)
        if parsed and parsed["id"]:
            return parsed["id"]
    s = str(sample_name)
    return s[:2] if len(s) >= 2 and s[:2].isalpha() else ""

def is_fu_sample(sample: str) -> bool:
    """
    Rozšířená detekce směsných (FU) vzorků.
    True = směs (obsahuje 'FU' nebo končí číselnou částí)
    False = srovnávací (koncovka 3–4 písmena, např. -UBP, -GIH)
    """
    if not sample:
        return False

    s = sample.upper().strip()

    # 1️⃣ klasické FU označení
    if "-FU" in s:
        return True

    # klasické buk označení
    if any(tag in s for tag in ["-ZZ", "-SK","-VK", "-OF", "-BF", "-BM"]):
        return False

    # 2️⃣ koncovka po poslední pomlčce
    m = re.search(r"-([A-Z0-9]+)$", s)
    if not m:
        return False  # nemá pomlčku → považujeme za srovnávací

    suffix = m.group(1)

    # 3️⃣ pouze písmena (3–4 znaky) → srovnávací
    if re.fullmatch(r"[A-Z]{3,4}", suffix):
        return False



def top2_alleles(alleles, min_ratio=0.3):
    """
    Vrátí maximálně dvě nejvyšší alely podle RFU.
    Druhá je zahrnuta pouze tehdy, pokud má alespoň
    `min_ratio` (např. 0.3 = 30 %) výšky první alely.

    Parametry:
        alleles : list[tuple(str, float)]  — [(allele, height)]
        min_ratio : float — minimální poměr výšky 2. alely k 1.

    Návratová hodnota:
        list[tuple(str, float)] — 1–2 relevantní alely
    """
    if not alleles:
        return []

    # Seřaď podle výšky RFU (od nejvyšší)
    sorted_alleles = sorted(alleles, key=lambda x: (x[1] or 0), reverse=True)

    # První (nejvyšší) alela je vždy zachována
    top = [sorted_alleles[0]]

    # Pokud existuje druhá a je dostatečně vysoká, přidej ji
    if len(sorted_alleles) > 1:
        top1_h = sorted_alleles[0][1] or 0
        top2_h = sorted_alleles[1][1] or 0
        if top2_h >= min_ratio * top1_h:
            top.append(sorted_alleles[1])

    return top

def normalize_allele_str(a):
    try:
        f = float(a)
        if f.is_integer():
            return str(int(f))
        else:
            return str(f).rstrip("0").rstrip(".")
    except Exception:
        return str(a)
    


def normalize_sample_name(name: str) -> str:
    """Ořízne, převede na velká písmena a sjednotí formátování názvu vzorku."""
    return str(name).strip().upper()

