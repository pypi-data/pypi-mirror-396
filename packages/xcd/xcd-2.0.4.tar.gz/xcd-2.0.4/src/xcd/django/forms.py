from email.policy import default
from django import forms
from xcd.core import XCD_kits

class ReportForm(forms.Form):
    txt_file = forms.FileField(label="Vyber soubor s profily DNA (GM-idx)", required=True)
    csv_files = forms.FileField(label="Vyber kvantifikační soubor(y)", required=False, widget=forms.ClearableFileInput())

    kit_autosomal = forms.ChoiceField(
        label="Pořadí lokusů podle kitu",
        choices=sorted([(k, k) for k, t in XCD_kits.KIT_TYPE.items() if t.upper() == "AUTOSOMAL"]),
        required=False
    )

    kit_y = forms.ChoiceField(
        label="Pořadí lokusů podle kitu (Y)",
        choices=sorted([(k, k) for k, t in XCD_kits.KIT_TYPE.items() if t.upper() == "Y"]),
        required=False
    )

    mode_filter = forms.ChoiceField(label="Typ odečtu", choices=[("VŠE", "Vše"), ("SOUPISKA", "Soupiska"),("PŘÍPAD", "Případ"), ("EXPERT", "Expert")], required=True)
    filter_value = forms.CharField(label="Zvol položku", required=False)

    highlight_major = forms.BooleanField(label="Zvýraznit majoritní složku", required=False)
    slope_effect = forms.BooleanField(label="Ski slope effect", required=False)

