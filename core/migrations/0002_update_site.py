"""
Migration de données : met à jour le Site par défaut (id=1)
de 'example.com' vers le domaine Atlas Énergies.
"""
from django.db import migrations


def update_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    Site.objects.filter(pk=1).update(
        domain='127.0.0.1:8000',
        name='Atlas Énergies',
    )


def revert_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    Site.objects.filter(pk=1).update(
        domain='example.com',
        name='example.com',
    )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(update_site, revert_site),
    ]
