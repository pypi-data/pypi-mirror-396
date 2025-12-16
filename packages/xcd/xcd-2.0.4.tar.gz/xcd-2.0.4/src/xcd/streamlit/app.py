import streamlit as st
import pandas as pd
import tempfile
import os
import sys
import base64

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core')))

from xcd.core import XCD_parsing, XCD_kits, XCD_utils, XCD_report

from importlib.metadata import version as pkg_version


def set_bg(image_file):
        with open(image_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            css= f"""
                <style>

                .stApp {{
                    background-image: url("data:image/png);base64,{encoded}");
                    background-size: cover;
                    background-repeat: no-repeat;
                    background-attachment: fixed;
                    background-position: relative;
                }}

                .stApp::before {{
                    content: "";
                    position: absolute;
                    top: 0; left: 0; right: 0; bottom: 0;
                    background-color: rgba(0, 0, 0, 0.9);
                    z-index: 0;
                }}
                            
                .block-container {{
                    position: relative;
                    z-index: 1;
                    padding-top: 0.7rem;
                    padding-bottom: 1.5rem;
                }}


                .stApp h1 {{
                    text-align: center;
                    font-size: 4rem;
                    font-weight: 700;
                    color: white !important;
                    margin-top: 0rem; 
                    margin-bottom: 0rem;
                }}

                </style>
                """

            st.markdown(css, unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(BASE_DIR, "XCD2_bg.jpg")

set_bg(image_path)
# ---------------------------
# Nastavení stránky
# ---------------------------
st.set_page_config(page_title="X-CELL DNA", layout="wide", initial_sidebar_state="expanded")

APP_VERSION = pkg_version("xcd")

import os

xlm_path = os.path.join(os.path.dirname(__file__), "..", "core", "XCD.xml")

if os.path.exists(xlm_path):
    with open(xlm_path, "rb") as f:
        xlm_bytes = f.read()

    st.download_button(
        label="📥 Stáhnout XCD.xml",
        data=xlm_bytes,
        file_name="XCD.xml",
        mime="application/xml",
        use_container_width=False,
    )
else:
    st.warning("Soubor XCD.xml nebyl nalezen ve složce aplikace.")


st.markdown(
    f"<div style='text-align:left; color:gray; font-size:0.9rem;'>v<b>{APP_VERSION}</b></div>",
    unsafe_allow_html=True
)
st.title("X-CELL DNA")

st.divider()

kit_names = [k for k, t in XCD_kits.KIT_TYPE.items() if t.upper() == "AUTOSOMAL"]
kit_names_y = [k for k, t in XCD_kits.KIT_TYPE.items() if t.upper() == "Y"]

pattern_options = {
    "identifikátor (např. TI25-01565-FU01)": "iiyydcccccdssnn",   # např. X-CELL styl
    "OKTE Ústí nad Labem (např. 1565-25-FU01)": "Cdyydssnn",            # např. jiná laborka
    "OKTE Hradec Králové (např. 1565-1)": "Ccdn",                      # např. jednoduchý formát
    "vlastní formát": "custom"
}

pattern_choice = st.selectbox(
    "Vyber formát názvů vzorků:",
    list(pattern_options.keys()),
    index=0
)

if pattern_choice == "vlastní formát":
    st.info("Vytvoř vlastní formát použitím těnchto značek: i =id, y =rok, c číslo, C =více čísel, s =typ, n =číslo vzorku, - =oddělovač (- nebo _).")
    pattern = st.text_input("Zadej vlastní formát:", placeholder="např. iiyy-cccc-ssnn (TI25-01565-FU01)")
else:
    pattern = pattern_options[pattern_choice]


# ---------------------------
# 1️⃣ Nahrání souborů
# ---------------------------
col1, col2 = st.columns(2)
with col1:
    txt_file = st.file_uploader("Vyber GeneMapper TXT soubor:", type=["txt"])

with col2:
    csv_files = st.file_uploader(
        "Vyber soubor s kvantifikací:", type=["csv", "xls", "xlsx"], accept_multiple_files=True)

st.divider()

col1, col2 = st.columns(2)
with col1:
    selected_kit = st.selectbox("Zvol autosomální kit, podle kterého budou řazeny lousy:", sorted([""] + kit_names), index = 0)

with col2:
    selected_kit_y = st.selectbox("Zvol Y kit, podle kterého budou řazeny lousy:", sorted([""] + kit_names_y), index = 0)

csv_paths = []
if csv_files:
    for uploaded in csv_files:
        tmp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded.name)[1])
                        
    tmp_csv.write(uploaded.getbuffer()) 
    tmp_csv.close() 
    csv_paths.append(tmp_csv.name)                                       


if txt_file:
    tmp_txt = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    tmp_txt.write(txt_file.getbuffer())
    tmp_txt.close()

    df = pd.read_csv(tmp_txt.name, sep="\t")
    panel = str(df["Panel"].dropna().iloc[0]) if "Panel" in df.columns else ""
    kit_norm = XCD_kits.normalize_kit_name(panel)
    kit_type = XCD_kits.KIT_TYPE.get(kit_norm, "AUTOSOMAL")

    # Automaticky vyber správný combobox
    if kit_type.upper() == "Y":
        used_kit = selected_kit_y
    else:
        used_kit = selected_kit

    results, run_header, df, log_list, kit = XCD_parsing.build_results(tmp_txt.name, used_kit)
    # seznamy případů a znalců
    
    cases, experts = XCD_parsing.parse_txt_for_options(tmp_txt.name)
    case_list = sorted(list(cases))
    case_map = {XCD_report.format_case_id(c): c for c in sorted(cases)}
    case_display_list = list(case_map.keys())
    expert_list = sorted(list(experts))
else:
    st.stop()


# ---------------------------
# 2️⃣ Filtry a nastavení
# ---------------------------

st.divider()

colu1, colu2 = st.columns(2)
with colu1:
    mode = st.radio("Zvol typ odečtu:",["SOUPISKA", "PŘÍPAD", "EXPERT"], horizontal=True)

with colu2:
    if mode == "PŘÍPAD":
        case_display = st.selectbox("Vyber případ:", case_display_list)
        value = case_map[case_display]
    elif mode == "EXPERT":
        value = st.selectbox("Vyber znalce:", expert_list)
    else:
        value = None

st.divider()

col1, col2= st.columns(2)
with col1:
    highlight_major = st.checkbox("Zvýraznit majoritní složku", value=False)
    slope_effect = st.checkbox("Použít slope effect", value=False)
    popis_vzorku = st.checkbox("Popisy vzorků", value=False)

    filtered_results = {}

    if mode == "PŘÍPAD":
        
        for cid in results.keys():
            cid_case = XCD_utils.get_case_id(cid)
            val_case = XCD_utils.get_case_id(value)

        filtered_results = {
            cid: smp
            for cid, smp in results.items()
            if XCD_utils.get_case_id(cid) == XCD_utils.get_case_id(value)
        }

    elif mode == "EXPERT" and value:
        filtered_results = {cid: smp for cid, smp in results.items() if any(s.startswith(value) for s in smp.keys())}
    else:
        filtered_results = results

with col2:\

    notes_dict = {}
    if popis_vzorku:
        with st.expander("Poznámky ke vzorkům", expanded=True):
            notes_dict = {}
            for case_id, samples in filtered_results.items():
                clean_case = XCD_report.format_case_id(case_id)
                st.markdown(f"{clean_case}")
                for sample in sorted([
                    s for s in samples.keys()
                    if not s.upper().endswith("LADDER")
                    and "PC" not in s.upper()
                    and "NC" not in s.upper()
                ]):
                    col1, col2 = st.columns([1,4], gap="small")
                    with col1:
                        st.markdown(f"<div style='text-align:center;font-weight:bold;font-size:0.95rem;'>{sample}</div>", unsafe_allow_html=True)
                    with col2:
                        notes_dict[sample] = st.text_input("", key=f"note_{sample}", label_visibility="collapsed")

st.divider()
# ---------------------------
# 3️⃣ Generování PDF
# ---------------------------
generate = st.button("Odečíst", width="stretch")

if generate:
    try:
        # dočasný výstupní soubor
        tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp_pdf.close()

        # Pokud existují results z XCD_parsing:
        try:
            st.write("Results count:", len(results))
            st.write("Case IDs in results:", list(results.keys())[:10])
        except Exception as e:
            st.write("Results not accessible:", e)

        # volání tvé funkce
        XCD_report.generate_report(
            tmp_txt.name,
            csv_paths,
            tmp_pdf.name,
            kit_name=used_kit,
            mode_filter=mode,
            filter_value=value,
            highlight_major=highlight_major,
            slope_effect=slope_effect,
            notes_dict=notes_dict,
            verze=APP_VERSION, 
            pattern=pattern,
            user_name=os.getlogin(),
            )

        with open(tmp_pdf.name, "rb") as f:
            pdf_bytes = f.read()

    except Exception as e:
        st.error(f"❌ Chyba při generování PDF: {e}")
