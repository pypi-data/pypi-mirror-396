from django.db import models

class Sample(models.Model):
    """
    Tabulka pro vzorky — každý vzorek má svůj unikátní název a popis.
    """
    id = models.AutoField(primary_key=True)
    idf = models.CharField(max_length=100, unique=True, verbose_name="Název vzorku")
    poznamka = models.TextField(blank=True, null=True, verbose_name="Popis vzorku")

    class Meta:
        managed = False
        db_table = "laborka_vzorek"           # můžeš změnit podle skutečného názvu tabulky

    def __str__(self):
        return self.name


class Quantification(models.Model):
    """
    Tabulka pro kvantifikační údaje — vazba na vzorek (Sample).
    """
    id = models.AutoField(primary_key=True)
    vzorek = models.ForeignKey(Sample, on_delete=models.CASCADE, db_column="vzorek_id")
    koncentrace = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    koncentrace_y = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    deg_a = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deg_y = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "laborka_kvantifikace"   # opět můžeš změnit podle své tabulky

    def __str__(self):
        return f"Kvantifikace {self.sample.name}"