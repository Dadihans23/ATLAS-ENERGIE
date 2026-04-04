"""
Migration corrective : ajoute centre_budgetaire_id à la table historique
générée par django-simple-history (manquée dans la migration manuelle 0002).

Dans les tables Historical*, les FK sont stockées comme IntegerField nullable
(pas de contrainte FK réelle — cohérence historique garantie par simple-history).
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('depenses', '0002_depensefraisgeneraux_add_projet'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicaldepensefraisgeneraux',
            name='centre_budgetaire_id',
            field=models.IntegerField(
                blank=True,
                null=True,
                db_index=True,
                verbose_name='Projet',
            ),
        ),
    ]
