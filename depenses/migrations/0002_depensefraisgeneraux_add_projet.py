"""
Migration : supprime tous les frais généraux existants (sans projet)
puis ajoute le FK obligatoire vers Projet.
"""
import django.db.models.deletion
from django.db import migrations, models


def supprimer_fg_existants(apps, schema_editor):
    """Vide la table avant d'ajouter la colonne NOT NULL."""
    DepenseFraisGeneraux = apps.get_model('depenses', 'DepenseFraisGeneraux')
    DepenseFraisGeneraux.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('depenses', '0001_initial'),
        ('projets', '0001_initial'),
    ]

    operations = [
        # 1. Vider les FG sans projet
        migrations.RunPython(supprimer_fg_existants, migrations.RunPython.noop),

        # 2. Ajouter le FK (table vide → pas de contrainte NOT NULL à résoudre)
        migrations.AddField(
            model_name='depensefraisgeneraux',
            name='centre_budgetaire',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='depenses_frais_generaux',
                to='projets.projet',
                verbose_name='Projet',
                db_index=True,
            ),
        ),
    ]
