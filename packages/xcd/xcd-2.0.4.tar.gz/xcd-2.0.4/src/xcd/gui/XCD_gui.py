import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os, json, csv
import pandas as pd
from PIL import Image, ImageTk
import re
from XCD_kits import KITS, KIT_TYPE
from XCD_report import generate_report
from XCD_parsing import parse_txt_for_options
import core.XCD_utils

import sys, os

def resource_path(relative_path):
    """Najde správnou cestu k přibalenému souboru (pro PyInstaller i pro .py)."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

CONFIG_FILE = resource_path("XCD_config.json")

def extract_samples_from_quant(path):
    samples = set()
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            if "TestSample" in row:
                if len(row) > 1:
                    samples.add(row[1].strip().upper())
    return samples

def save_last_config(kit_name, kit_name_y, highlight_major, slope_effect, popis_vzorku):
    data = {
        "last_kit": kit_name,
        "last_kit_y": kit_name_y,
        "highlight_major": bool(highlight_major),
        "slope_effect": bool(slope_effect),
        "popis_vzorku": bool(popis_vzorku)
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

def load_last_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def display_case_id(case_id: str) -> str:
    import re
    m = re.search(r"(\d{3,5})", case_id)
    return m.group(1).lstrip("0") if m else case_id

def simplify_case_id(case_id: str) -> str:
    import re

    parts = case_id.split("-")

    # --- Pravidlo 1: dvě pomlčky (např. TI25-02035-FU01)
    if len(parts) >= 3:
        middle = parts[1]
        case_num = re.sub(r"\D", "", middle).lstrip("0")  # číslo bez nul
        year_match = re.search(r"\d{2}", parts[0])
        year_val = year_match.group(0) if year_match else ""
        return f"{case_num}/{year_val}" if year_val else case_num

    # --- Pravidlo 2: začíná písmeny (např. TI25-02828)
    if re.match(r"^[A-Za-z]", case_id):
        year = case_id[2:4]
        num_match = re.search(r"(\d{3,5})$", case_id)
        case_num = num_match.group(1).lstrip("0") if num_match else case_id
        return f"{case_num}/{year}"

    # --- Pravidlo 3: začíná číslem (např. 146-25-FU01)
    if re.match(r"^\d", case_id):
        parts = case_id.split("-")
        if len(parts) >= 2:
            num = re.sub(r"\D", "", parts[0]).lstrip("0")
            year = re.sub(r"\D", "", parts[1])[:2]
            return f"{num}/{year}"
        else:
            return case_id

    return case_id

    
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.verze = "XCD v2.0.0"
        self.title(self.verze)
        self.resizable(False, False)

        w, h = 600, 400
        ws, hs = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (ws // 2) - (w // 2), (hs // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # full paths + zobrazení názvů v entry
        self.txt_fullpath = None
        self.out_fullpath = None
        self.csv_paths = []          # list of full paths
        self.samples_from_profiles = set()

        # ikonka a pozadí
        try:
            self.iconphoto(False, tk.PhotoImage(file=resource_path("XCD_logo.png")))
        except Exception:
            pass
        try:
            self.bg_img = ImageTk.PhotoImage(Image.open(resource_path("XCD_bg.jpg")))
            tk.Label(self, image=self.bg_img).place(relwidth=1, relheight=1)
        except Exception:
            pass

        frame = tk.Frame(self, bg="#0B2D41", border=3, relief="ridge", padx=10, pady=10)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # tk proměnné pro entry (jen názvy souborů)
        self.txt_path = tk.StringVar()
        self.csv_path = tk.StringVar()
        self.out_path = tk.StringVar()

        self.filter_mode = tk.StringVar(value="SOUPISKA")
        self.filter_value = tk.StringVar(value="")
        self.kit_choice = tk.StringVar(value="26Plex QS")

        self.highlight_major = tk.BooleanVar(value=False)
        self.slope_effect = tk.BooleanVar(value=False)
        self.popis_vzorku = tk.BooleanVar(value=False)

        self.case_options, self.expert_options = [], []
        self.case_map = {}

        barva_widget = "#0B2D41"
        barva_button = "#2E363D"

        # řádky GUI
        tk.Label(frame, text="Soubor z GM-IDX:", bg=barva_widget, fg="#DDDDDD")\
            .grid(row=0, column=0, sticky="e", padx=8, pady=8)
        tk.Entry(frame, textvariable=self.txt_path, width=35)\
            .grid(row=0, column=1, columnspan=2, padx=0)
        tk.Button(frame, text=" ... ", command=self.pick_txt, bg=barva_button, fg="white")\
            .grid(row=0, column=3, padx=10)

        tk.Label(frame, text="Soubor z kvantifikace:", bg=barva_widget, fg="#DDDDDD")\
            .grid(row=1, column=0, sticky="e", padx=8, pady=8)
        tk.Entry(frame, textvariable=self.csv_path, width=35)\
            .grid(row=1, column=1, columnspan=2, padx=0)
        self.btn_csv = tk.Button(
            frame,
            text=" ... ",
            command=self.pick_csv,
            bg=barva_button,
            fg="white",
            state="disabled"   # <- zamčeno při startu
        )
        self.btn_csv.grid(row=1, column=3, padx=10)


        tk.Label(frame, text="Pořadí podle kitu (A):", bg=barva_widget, fg="#DDDDDD")\
            .grid(row=3, column=0, sticky="e", padx=8, pady=8)
        self.cb_kit_auto = ttk.Combobox(frame, values=[k for k in KITS if KIT_TYPE[k] == "AUTOSOMAL"],
                                        state="readonly", width=12)
        self.cb_kit_auto.grid(row=3, column=1, sticky="w")

        tk.Label(frame, text="Pořadí podle kitu (Y):", bg=barva_widget, fg="#DDDDDD")\
            .grid(row=4, column=0, sticky="e", padx=8, pady=8)
        self.cb_kit_y = ttk.Combobox(frame, values=[k for k in KITS if KIT_TYPE[k] == "Y"],
                                     state="readonly", width=12)
        self.cb_kit_y.grid(row=4, column=1, sticky="w")

        tk.Label(frame, text="Filtr:", bg=barva_widget, fg="#DDDDDD")\
            .grid(row=5, column=0, sticky="e", padx=8, pady=8)
        self.cb_mode = ttk.Combobox(frame, textvariable=self.filter_mode,
                                    values=["SOUPISKA", "PŘÍPAD", "EXPERT"], state="readonly", width=12)
        self.cb_mode.grid(row=5, column=1, sticky="w")
        self.cb_mode.bind("<<ComboboxSelected>>", self.on_filter_change)

        self.cb_value = ttk.Combobox(frame, textvariable=self.filter_value, values=[], state="disabled", width=12)
        self.cb_value.grid(row=6, column=1, sticky="w")


        tk.Checkbutton(frame, text="Majoritní složka", variable=self.highlight_major,
                       bg=barva_widget, fg="#DDDDDD", selectcolor=barva_widget)\
            .grid(row=3, column=2, sticky="w", padx=5, pady=10)
        tk.Checkbutton(frame, text="Slope effect", variable=self.slope_effect,
                       bg=barva_widget, fg="#DDDDDD", selectcolor=barva_widget)\
            .grid(row=4, column=2, sticky="w", padx=5)
        self.popis_vzorku = tk.BooleanVar(value=False)
        tk.Checkbutton(frame, text="Popisy vzorků", variable=self.popis_vzorku,
                    bg=barva_widget, fg="#DDDDDD", selectcolor=barva_widget).grid(row=5, column=2, sticky="w", padx=5)
        
        tk.Button(frame, text="               Odečíst               ", command=self.run_generate,
                  bg=barva_button, fg="white").grid(row=8, column=2, columnspan=4, pady=20)

        tk.Button(
            frame,
            text="↓ GM-IDX Report Settings",
            command=self.download_existing_xml,
            bg=barva_button,
            fg="white"
        ).grid(row=8, column=0, pady=20)

        # načti poslední volby
        cfg = load_last_config()
        last_kit = cfg.get("last_kit")
        last_kit_y = cfg.get("last_kit_y")
        if last_kit and last_kit in self.cb_kit_auto["values"]:
            self.cb_kit_auto.set(last_kit)
        if last_kit_y and last_kit_y in self.cb_kit_y["values"]:
            self.cb_kit_y.set(last_kit_y)
        self.highlight_major.set(cfg.get("highlight_major", False))
        self.slope_effect.set(cfg.get("slope_effect", False))
        self.popis_vzorku.set(cfg.get("popis_vzorku", False))

    def download_existing_xml(self):
        """Umožní uživateli stáhnout (uložit) přibalený XML soubor"""
        from tkinter import filedialog, messagebox
        import shutil, os, sys

        def resource_path(relative_path):
            """Vrací cestu k resource (funguje i z .exe)"""
            try:
                base_path = sys._MEIPASS  # když běží jako .exe
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)

        # cesta k souboru v projektu nebo v .exe
        src = resource_path("XCD.xml")

        if not os.path.exists(src):
            messagebox.showerror("Chyba", "Soubor XCD.xml nebyl nalezen.")
            return

        # vybrat kam se má uložit
        dst = filedialog.asksaveasfilename(
            title="Uložit XCD.xml jako",
            initialfile="XCD.xml",
            defaultextension=".xml",
            filetypes=[("XML soubory", "*.xml"), ("Všechny soubory", "*.*")]
        )

        if not dst:
            return

        shutil.copy(src, dst)

    # ----- Handlery -----
    def pick_txt(self):
        from tkinter import filedialog, messagebox
        import pandas as pd

        path = filedialog.askopenfilename(
            title="Vyber GeneMapper TXT",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return

        # ulož fullpath + do entry jen basename
        self.txt_fullpath = path
        self.txt_path.set(os.path.basename(path))

        # navrhni defaultní výstup do stejné složky
        base, _ = os.path.splitext(path)
        if not self.out_fullpath:
            self.out_fullpath = base + "_tabulka.pdf"
            self.out_path.set(os.path.basename(self.out_fullpath))

        # načíst dataframe
        try:
            df = pd.read_csv(path, sep="\t")
        except Exception as e:
            messagebox.showerror("Chyba", f"Soubor se nepodařilo načíst:\n{e}")
            return

        # načíst vzorky z TXT (normalizované)
        samples = df[~df["Sample Name"].isin(["LADDER", "PC", "NC"])]["Sample Name"].unique()
        self.samples_from_profiles = {core.XCD_utils.normalize_sample_name(s) for s in samples}

        # --- NOVÁ KONTROLA: lokusy s 40 alelami/OL ---
        warnings = []
        allele_cols = [c for c in df.columns if c.startswith("Allele ")]
        for _, row in df.iterrows():
            sample = row["Sample Name"]
            if sample in ["LADDER", "PC", "NC"]:
                continue  # ignorujeme ladder a kontroly
            marker = row["Marker"]
            non_empty = sum(1 for c in allele_cols if pd.notna(row.get(c)))
            if non_empty >= 40:
                warnings.append(f"{sample} – {marker}")

        if warnings:
            msg = "Pozor: Nalezeny lokusy s 20 alelami/OL!\n\n"
            msg += "\n".join(warnings[:15])
            if len(warnings) > 15:
                msg += f"\n... a další ({len(warnings)-15})"
            messagebox.showwarning("Upozornění", msg)

        # --- AUTOMATICKÁ DETEKCE TYPU KITU (Y vs AUTOSOMÁLNÍ) ---
        try:
            if "Panel" in df.columns and not df["Panel"].isna().all():
                panel_value = str(df["Panel"].dropna().iloc[0]).upper()

                # detekce Y kitu
                if any(tag in panel_value for tag in ["YFILER", "Y23", "Y28", "YPLEX", "Y-"]):

                    self.cb_kit_y.configure(state="readonly")
                    self.cb_kit_auto.configure(state="disabled")
                    #print(f"🧬 Detekován Y-kit: {panel_value}")

                else:

                    self.cb_kit_auto.configure(state="readonly")
                    self.cb_kit_y.configure(state="disabled")
                    #print(f"🧬 Detekován autosomální kit: {panel_value}")

            else:
                # nelze zjistit kit → oba comboboxy aktivní
                self.cb_kit_auto.configure(state="readonly")
                self.cb_kit_y.configure(state="readonly")
                print("⚠️ Nelze určit typ kitu z TXT, oba comboboxy ponechány aktivní.")
        except Exception as e:
            print(f"⚠️ Chyba při detekci kitu: {e}")

        # CASE / EXPERT pro filtr
        cases, experts = parse_txt_for_options(path)
        self.case_options = sorted(list(cases))
        self.expert_options = sorted(list(experts))
        self.refresh_value_options()

        # odemknout tlačítko pro CSV, až když je TXT načteno
        self.btn_csv.config(state="normal")



    def pick_csv(self):
        path = filedialog.askopenfilename(
            title="Vyber kvantifikační CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not path:
            return

        # přidej do seznamu (fullpath) a do entry zobraz jen názvy
        self.csv_paths.append(path)
        self.csv_path.set("; ".join(os.path.basename(p) for p in self.csv_paths))

        # kontrola přítomnosti vzorků v kvantifikaci (porovnání normalizovaných jmen)
        samples_in_csv = extract_samples_from_quant(path)
        samples_in_csv = {core.XCD_utils.normalize_sample_name(s) for s in samples_in_csv}
        missing = self.samples_from_profiles - samples_in_csv

        if missing:
            msg = (
                f"Chybí kvantifikace pro {len(missing)} vzorků:\n"
                + ", ".join(sorted(list(missing))[:10])
                + ("..." if len(missing) > 10 else "")
                + "\n\nChceš nahrát další CSV?"
            )
            if messagebox.askyesno("Chybějící vzorky", msg):
                self.pick_csv()  # rekurzivní výzva

    def pick_out(self):
        path = filedialog.asksaveasfilename(
            title="Uložit výstupní PDF jako", defaultextension=".pdf", filetypes=[("PDF", "*.pdf")]
        )
        if not path:
            return
        self.out_fullpath = path
        self.out_path.set(os.path.basename(path))

    def on_filter_change(self, _=None):
        self.refresh_value_options()


    def refresh_value_options(self):
        mode = self.filter_mode.get()
        if mode == "PŘÍPAD":
            display_values = [display_case_id(c) for c in self.case_options]
            self.case_map = {display_case_id(c): c for c in self.case_options}
            self.cb_value["values"] = sorted(display_values)
            self.cb_value["state"] = "readonly"
            self.filter_value.set(display_values[0] if display_values else "")
        elif mode == "EXPERT":
            self.cb_value["values"] = sorted(self.expert_options)
            self.cb_value["state"] = "readonly"
            self.filter_value.set(self.expert_options[0] if self.expert_options else "")
        else:
            self.cb_value["values"] = []
            self.cb_value["state"] = "disabled"
            self.filter_value.set("")

    def ask_notes_for_case(self, case_id, samples):
        import tkinter as tk

        short_case = simplify_case_id(case_id)

        notes = {}
        win = tk.Toplevel(self)
        win.title(f"Popis vzorku k {short_case}")

        # dynamická výška podle počtu vzorků
        row_height = 30   # px na jeden řádek
        h = min(100 + len(samples) * row_height, 600)  # max 600 px
        w = 300

        ws, hs = win.winfo_screenwidth(), win.winfo_screenheight()
        x, y = (ws // 2) - (w // 2), (hs // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.configure(bg="#0B2D41")

        frame = tk.Frame(win, bg="#0B2D41")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        entries = {}
        
        tk.Label(frame, text=f"{short_case}", bg="#0B2D41", fg="#DDDDDD", font=("Calibri")).pack(anchor="w", pady=(0,5))

        for s in samples:
            row = tk.Frame(frame)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=s, bg="#0B2D41", fg="#DDDDDD", width=15, anchor="w").pack(side="left")
            e = tk.Entry(row, width=20)
            e.pack(side="left", fill="x", expand=True)
            entries[s] = e

        def on_ok():
            for s, e in entries.items():
                notes[s] = e.get().strip()
            win.destroy()

        btn_ok = tk.Button(frame, text="   OK   ", bg="#2E363D", fg="#DDDDDD", command=on_ok)
        btn_ok.pack(pady=10)

        if entries:
            first_entry = list(entries.values())[0] 
            win.after(100, lambda:
            first_entry.focus_set())

        win.bind("<Return>", lambda
        event=None: on_ok())

        win.grab_set()
        win.focus_force()
        win.wait_window()

        return notes


    def run_generate(self):
        try:
            if not self.txt_fullpath:
                messagebox.showerror("Chyba", "Vyber GeneMapper TXT soubor.")
                return

            mode = self.filter_mode.get()
            value = self.filter_value.get().strip()

            # pokud jde o CASE, použij původní case_id
            if mode == "PŘÍPAD" and hasattr(self, "case_map") and value in self.case_map:
                value = self.case_map[value]

            # --- ROZHODNUTÍ, KTERÝ COMBOBOX JE AKTIVNÍ ---
            kit = None
            auto_state = str(self.cb_kit_auto.cget("state"))
            y_state = str(self.cb_kit_y.cget("state"))

            if "readonly" in y_state and "disabled" in auto_state:
                kit = self.cb_kit_y.get()

            elif "readonly" in auto_state and "disabled" in y_state:
                kit = self.cb_kit_auto.get()

            else:
                # fallback – pokud by nebyl zamčen žádný (např. ručně)
                kit = self.cb_kit_auto.get() or self.cb_kit_y.get()

            if not kit:
                messagebox.showerror("Chyba", "Vyber kit (autozomální nebo Y).")
                return

            # --- Poznámky k vzorkům ---
            notes_dict = None
            if self.popis_vzorku.get():
                import pandas as pd
                df = pd.read_csv(self.txt_fullpath, sep="\t")
                samples = df[~df["Sample Name"].isin(["LADDER", "PC", "NC"])]["Sample Name"].unique()

                # vyfiltruj podle módu
                if mode == "PŘÍPAD" and value:
                    samples = [s for s in samples if value in s]
                elif mode == "EXPERT" and value:
                    samples = [s for s in samples if s.startswith(value)]

                # seskupení podle case_id
                notes_dict = {}
                for case in sorted({core.XCD_utils.get_case_id(s) for s in samples}):
                    case_samples = [s for s in samples if core.XCD_utils.get_case_id(s) == case]
                    if case_samples:
                        notes_dict[case] = self.ask_notes_for_case(case, case_samples)

            # --- Zavoláme generate_report ---
            generate_report(
                self.txt_fullpath,
                self.csv_paths,
                self.out_fullpath,
                kit_name=kit,
                mode_filter=mode,
                filter_value=value,
                highlight_major=self.highlight_major.get(),
                slope_effect=self.slope_effect.get(),
                notes_dict=notes_dict,
                verze=self.verze,
            )

            # --- Uložení poslední konfigurace ---
            kit_auto = self.cb_kit_auto.get()
            kit_y = self.cb_kit_y.get()
            save_last_config(
                kit_auto,
                kit_y,
                self.highlight_major.get(),
                self.slope_effect.get(),
                self.popis_vzorku.get()
            )

        except Exception as e:
            messagebox.showerror("Chyba", f"Něco se nepovedlo:\n{e}")



if __name__ == "__main__":
    App().mainloop()
