from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_add_dt_df_roles'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_backend', models.CharField(default='django.core.mail.backends.smtp.EmailBackend', max_length=150, verbose_name='Backend email')),
                ('email_host', models.CharField(default='smtp.gmail.com', max_length=255, verbose_name='Serveur SMTP')),
                ('email_port', models.PositiveIntegerField(default=465, verbose_name='Port SMTP')),
                ('email_use_ssl', models.BooleanField(default=True, verbose_name='SSL (port 465)')),
                ('email_use_tls', models.BooleanField(default=False, verbose_name='TLS (port 587)')),
                ('email_host_user', models.EmailField(blank=True, max_length=254, verbose_name='Compte expéditeur (email)')),
                ('email_host_password', models.CharField(blank=True, max_length=255, verbose_name='Mot de passe / App Password')),
                ('default_from_email', models.CharField(blank=True, help_text='Exemple : Atlas Énergies <noreply@atlas-energies.ci>', max_length=255, verbose_name="Nom et adresse d'expédition")),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Dernière mise à jour')),
            ],
            options={
                'verbose_name': 'Configuration email',
                'verbose_name_plural': 'Configuration email',
            },
        ),
    ]
