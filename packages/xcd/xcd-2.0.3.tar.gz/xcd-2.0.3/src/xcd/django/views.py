from tracemalloc import reset_peak
import pandas as pd
import re
import io
from .forms import ReportForm
from xcd.core import XCD_report, XCD_parsing, XCD_db, XCD_utils
import tempfile, os, re
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, FileResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render
from importlib.metadata import version as pkg_version
import uuid, tempfile, os, threading
from django.core.cache import cache
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, FileResponse, Http404, HttpResponseBadRequest
from xcd.core import XCD_report, XCD_parsing, XCD_db

try:
    from xcd import XCD_VERSION  # vezme z __init__.py
except Exception:
    # pojistka když by balíček ještě nebyl instalován
    try:
        from importlib.metadata import version as _pkg_version
        XCD_VERSION = _pkg_version("xcd")
    except Exception:
        XCD_VERSION = "dev"

CACHE_TTL = 60 * 30  # 30 minut

def _cache_key(job_id, suffix):
    return f"xcd_job:{job_id}:{suffix}"

def _set_progress(job_id, val):
    cache.set(_cache_key(job_id, "progress"), int(val), CACHE_TTL)

def _get_progress(job_id):
    return int(cache.get(_cache_key(job_id, "progress"), 0))

def _set_output(job_id, path):
    cache.set(_cache_key(job_id, "pdf_path"), path, CACHE_TTL)

def _get_output(job_id):
    return cache.get(_cache_key(job_id, "pdf_path"))

def _worker_generate(job_id, txt_path, used_kit_auto, used_kit_y, mode_filter, filter_value, highlight_major, slope_effect, request_user):
    try:
        _set_progress(job_id, 1)  # early
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            pdf_path = tmp_pdf.name

        results_all, run_headers, df_all, logs_all, kits_all, sample_meta_all = XCD_parsing.build_all_results(txt_path)
        _set_progress(job_id, 5)

        filtered = XCD_report.apply_filter(results_all, mode_filter, filter_value, pattern="", sample_meta_all=sample_meta_all, run_headers=run_headers)
        sample_names = sorted({s for _, smap in filtered.items() for s in smap.keys()})
        db_data = XCD_db.load_db_data_for_samples(sample_names)
        _set_progress(job_id, 10)

        def _cb(p): _set_progress(job_id, p)

        XCD_report.generate_report(
            txt_path, None, pdf_path,
            kit_name=used_kit_auto,
            kit_name_auto=used_kit_auto,
            kit_name_y=used_kit_y,
            mode_filter=mode_filter, filter_value=filter_value,
            highlight_major=highlight_major, slope_effect=slope_effect,
            verze=XCD_VERSION,
            user_name=(request_user.get_full_name() or request_user.username),
            db_data=db_data, header_text=None,
            progress_cb=_cb,
        )
        _set_output(job_id, pdf_path)
        _set_progress(job_id, 100)
    except Exception as e:
        import traceback; traceback.print_exc()
        _set_progress(job_id, 100)


@require_POST

def start_report(request):
    try:
        txt_file = request.FILES.get("txt_file")
        if not txt_file:
            return HttpResponseBadRequest("Chybí TXT soubor.")

        used_kit_auto = request.POST.get("kit_autosomal") or ""
        used_kit_y    = request.POST.get("kit_y") or ""
        mode_filter   = request.POST.get("mode_filter") or "VŠE"
        filter_value  = request.POST.get("filter_value") or ""
        highlight_major = bool(request.POST.get("highlight_major"))
        slope_effect    = bool(request.POST.get("slope_effect"))

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_txt:
            for chunk in txt_file.chunks():
                tmp_txt.write(chunk)
            tmp_txt_path = tmp_txt.name

        job_id = uuid.uuid4().hex
        _set_progress(job_id, 0)
        cache.delete(_cache_key(job_id, "pdf_path"))

        t = threading.Thread(
            target=_worker_generate,
            args=(job_id, tmp_txt_path, used_kit_auto, used_kit_y, mode_filter, filter_value, highlight_major, slope_effect, request.user),
            daemon=True
        )
        t.start()

        return JsonResponse({"job_id": job_id})
    except Exception as e:
        import traceback; traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


def progress(request, job_id):
    return JsonResponse({"progress": _get_progress(job_id)})

def download_report(request, job_id):
    path = _get_output(job_id)
    if not path or not os.path.exists(path):
        raise Http404("Soubor není připraven.")
    # volitelně: smazat progress a/nebo file po odeslání
    return FileResponse(open(path, "rb"), as_attachment=True, filename=f"XCD_report_{job_id}.pdf")

def download_xml(request):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    xml_path = os.path.join(base_dir,"core","XCD.xml")


    if os.path.exists(xml_path):
        return FileResponse(open(xml_path, "rb"), as_attachment=True, filename="XCD.xml")
    else: raise Http404("Soubor XCD.xml nebyl nalezen.")


def load_case_and_expert_options(request):
    # 1) validace vstupu
    txt = request.FILES.get("txt_file")
    if not txt:
        return JsonResponse({"cases": [], "experts": [], "runs": []})

    # 2) načtení jen kvůli seznamům (rychlé)
    try:
        df = pd.read_csv(txt, sep="\t")
    except Exception as e:
        return JsonResponse({"cases": [], "experts": [], "runs": [], "error": str(e)}, status=400)

    # ignoruj technické vzorky
    df = df[~df["Sample Name"].isin(["LADDER", "PC", "NC"])].copy()

    # PŘÍPAD = číslo/rok z názvu (např. 2035/25)
    def parse_case(s):
        # očekává vzorek typu "TF24-02035-FU01" nebo "TS16-03352-FU01"
        try:
            parts = s.strip().split("-")
            num = parts[1].lstrip("0")
            yy  = parts[0][2:4]
            return f"{num}/{yy}"
        except Exception:
            return ""

    # EXPERT = první 2 písmena prvního segmentu (ať má pomlčku)
    def parse_expert(s):
        if "-" not in s:
            return ""
        seg0 = s.split("-")[0].lstrip()
        return seg0[:2] if seg0[:2].isalpha() else ""

    # 3) poskládej unikátní hodnoty
    samples = df["Sample Name"].dropna().astype(str).unique().tolist()
    cases   = sorted({c for s in samples if (c := parse_case(s))})
    experts = sorted({e for s in samples if (e := parse_expert(s))})

    runs = []
    if "Run Name" in df.columns:
        runs = sorted({str(r).strip() for r in df["Run Name"].dropna().unique().tolist()})

    # 4) vrať JSON pro JS
    return JsonResponse({
        "cases":   cases,
        "experts": experts,
        "runs":    runs,
        # mapování není nutné (label==value), ale může se hodit do budoucna:
        "case_map": {c: c for c in cases},
    })

def index(request):
    XCD_VERSION = pkg_version("xcd")
    pdf_path = None
    form = ReportForm()

    if request.method == "POST":
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            # 1) Ulož TXT do dočasného souboru
            txt_file = request.FILES["txt_file"]
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_txt:
                for chunk in txt_file.chunks():
                    tmp_txt.write(chunk)
                tmp_txt_path = tmp_txt.name

            # 2) Zvol kit (uživatelský výběr přepíše autodetekci)
            used_kit_auto = form.cleaned_data.get("kit_autosomal")
            used_kit_y = form.cleaned_data.get("kit_y")
            # 3) Rozparsuj celý TXT na více runů (soupisek)
            results_all, run_headers, df_all, logs_all, kits_all, sample_meta_all = XCD_parsing.build_all_results(tmp_txt_path)

            # 4) Načti filtr z formuláře
            mode_filter  = form.cleaned_data.get("mode_filter") or "VŠE"      # "VŠE" | "SOUPISKA" | "PŘÍPAD" | "EXPERT"
            filter_value = form.cleaned_data.get("filter_value") or ""

            # 5) Aplikuj filtr na results (používáme helper v XCD_report)
            filtered = XCD_report.apply_filter(results_all, mode_filter, filter_value, pattern="", sample_meta_all=sample_meta_all, run_headers=run_headers)

            # 6) Získáme seznam vzorků pro načtení doplňkových dat z DB
            sample_names = sorted({sample for _, smap in filtered.items() for sample in smap.keys()})

            db_data = XCD_db.load_db_data_for_samples(sample_names)

            # 7) Připrav cílový PDF soubor a vygeneruj report
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                pdf_path = tmp_pdf.name

            # Pro SOUPISKA nastav správnou hlavičku dle zvoleného runu
            header_text = run_headers.get(filter_value) if mode_filter == "SOUPISKA" else None

            XCD_report.generate_report(
                tmp_txt_path,
                None,
                pdf_path,
                kit_name=used_kit_auto,
                kit_name_auto=used_kit_auto,
                kit_name_y=used_kit_y,
                mode_filter=mode_filter,
                filter_value=filter_value,
                highlight_major=form.cleaned_data.get("highlight_major"),
                slope_effect=form.cleaned_data.get("slope_effect"),
                verze=XCD_VERSION,
                user_name=(request.user.get_full_name() or request.user.username),
                db_data=db_data,
                header_text=header_text,      # XCD_report si ji použije, když je předaná
            )

    return render(request,"xcd/index.html",{"form": form,"pdf_path": pdf_path,"XCD_VERSION": XCD_VERSION,},
    )