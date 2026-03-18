"""
Commande de gestion : peuple la base avec des donnees de demonstration.

Usage :
    python manage.py create_demo_data
    python manage.py create_demo_data --flush   # vide d'abord la base

Cree :
  - 1 Chef d'Agence  : chef@atlas-energies.ci / Atlas2024!
  - 2 Agents         : agent1@atlas-energies.ci / Atlas2024!
                       agent2@atlas-energies.ci / Atlas2024!
  - 3 Projets avec budgets
  - 8 Depenses d'exploitation
  - 5 Frais generaux
"""
from decimal import Decimal
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from core.models import CustomUser
from projets.models import Projet
from depenses.models import DepenseExploitation, DepenseFraisGeneraux


PASSWORD = 'Atlas2024!'


class Command(BaseCommand):
    help = 'Cree des donnees de demonstration pour Atlas Energies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Supprime toutes les donnees existantes avant creation',
        )

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write('Suppression des donnees existantes...')
            DepenseExploitation.objects.all().delete()
            DepenseFraisGeneraux.objects.all().delete()
            Projet.objects.all().delete()
            CustomUser.objects.filter(is_superuser=False).delete()
            self.stdout.write('  [OK] Base videe')

        # ── Utilisateurs ──────────────────────────────────────────────────────
        self.stdout.write('\nCreation des utilisateurs...')

        chef, created = CustomUser.objects.get_or_create(
            email='chef@atlas-energies.ci',
            defaults={
                'first_name': 'Kouame',
                'last_name': 'BROU',
                'role': CustomUser.Role.CHEF,
                'is_staff': True,
            }
        )
        if created:
            chef.set_password(PASSWORD)
            chef.save()
        self.stdout.write(f'  [OK] Chef : {chef.email}')

        agent1, created = CustomUser.objects.get_or_create(
            email='agent1@atlas-energies.ci',
            defaults={
                'first_name': 'Adjoua',
                'last_name': 'KOFFI',
                'role': CustomUser.Role.AGENT,
            }
        )
        if created:
            agent1.set_password(PASSWORD)
            agent1.save()
        self.stdout.write(f'  [OK] Agent1 : {agent1.email}')

        agent2, created = CustomUser.objects.get_or_create(
            email='agent2@atlas-energies.ci',
            defaults={
                'first_name': 'Yao',
                'last_name': 'ASSI',
                'role': CustomUser.Role.AGENT,
            }
        )
        if created:
            agent2.set_password(PASSWORD)
            agent2.save()
        self.stdout.write(f'  [OK] Agent2 : {agent2.email}')

        # ── Projets ───────────────────────────────────────────────────────────
        self.stdout.write('\nCreation des projets...')

        projets_data = [
            {
                'nom': 'ELECTRIFICATION RURALE BONDOUKOU',
                'designation': 'Extension du reseau electrique dans les villages de la region de Gontougo',
                'budget_etude': Decimal('8500000'),
                'budget_materiel_equipement': Decimal('45000000'),
                'budget_logistique': Decimal('12000000'),
                'budget_soustraitance': Decimal('30000000'),
                'budget_frais_mission': Decimal('4500000'),
            },
            {
                'nom': 'REHABILITATION POSTE HTA KORHOGO',
                'designation': 'Rehabilitation complete du poste haute tension de Korhogo phase 2',
                'budget_etude': Decimal('5000000'),
                'budget_materiel_equipement': Decimal('22000000'),
                'budget_logistique': Decimal('6000000'),
                'budget_soustraitance': Decimal('15000000'),
                'budget_frais_mission': Decimal('3000000'),
            },
            {
                'nom': 'AUDIT ENERGETIQUE ZONES NORD',
                'designation': "Audit de consommation energetique des installations industrielles du nord ivoirien",
                'budget_etude': Decimal('12000000'),
                'budget_materiel_equipement': Decimal('3500000'),
                'budget_logistique': Decimal('8000000'),
                'budget_soustraitance': Decimal('5000000'),
                'budget_frais_mission': Decimal('6500000'),
            },
        ]

        projets = []
        for data in projets_data:
            p, created = Projet.objects.get_or_create(
                nom=data['nom'],
                defaults={**data, 'created_by': chef, 'is_active': True},
            )
            projets.append(p)
            self.stdout.write(f'  [OK] {p.nom}')

        # ── Depenses d'exploitation ───────────────────────────────────────────
        self.stdout.write("\nCreation des depenses d'exploitation...")

        today = date.today()
        exploitation_data = [
            {
                'centre_budgetaire': projets[0],
                'ligne_budgetaire': DepenseExploitation.LigneBudgetaire.ETUDE,
                'nature_depense': DepenseExploitation.NatureDepense.FACTURE,
                'libelle': 'Etude topographique et geotechnique tranche 1',
                'devise': 'XOF', 'montant': Decimal('2800000'),
                'fournisseur': 'CABINET ETUDES ABIDJAN',
                'date_saisie': today - timedelta(days=20),
                'created_by': agent1,
            },
            {
                'centre_budgetaire': projets[0],
                'ligne_budgetaire': DepenseExploitation.LigneBudgetaire.MATERIEL,
                'nature_depense': DepenseExploitation.NatureDepense.BON_COMMANDE,
                'libelle': 'Cables HTA 95mm aluminium 500ml',
                'devise': 'XOF', 'montant': Decimal('12500000'),
                'fournisseur': 'NEXANS COTE D IVOIRE',
                'date_saisie': today - timedelta(days=15),
                'created_by': agent1,
            },
            {
                'centre_budgetaire': projets[0],
                'ligne_budgetaire': DepenseExploitation.LigneBudgetaire.LOGISTIQUE,
                'nature_depense': DepenseExploitation.NatureDepense.FACTURE,
                'libelle': 'Location camion plateau 20T 5 voyages Bondoukou',
                'devise': 'XOF', 'montant': Decimal('3200000'),
                'fournisseur': 'TRANSPORT KONE ET FILS',
                'date_saisie': today - timedelta(days=12),
                'created_by': agent2,
            },
            {
                'centre_budgetaire': projets[0],
                'ligne_budgetaire': DepenseExploitation.LigneBudgetaire.FRAIS_MISSION,
                'nature_depense': DepenseExploitation.NatureDepense.DEMANDE_ACHAT,
                'libelle': 'Per diem equipe terrain 3 personnes x 7 jours',
                'devise': 'XOF', 'montant': Decimal('630000'),
                'fournisseur': '',
                'date_saisie': today - timedelta(days=10),
                'created_by': agent2,
            },
            {
                'centre_budgetaire': projets[1],
                'ligne_budgetaire': DepenseExploitation.LigneBudgetaire.MATERIEL,
                'nature_depense': DepenseExploitation.NatureDepense.FACTURE,
                'libelle': 'Transformateur HTB/HTA 630 kVA',
                'devise': 'EUR', 'montant': Decimal('8500'),
                'fournisseur': 'ABB FRANCE',
                'date_saisie': today - timedelta(days=8),
                'created_by': agent1,
            },
            {
                'centre_budgetaire': projets[1],
                'ligne_budgetaire': DepenseExploitation.LigneBudgetaire.SOUSTRAITANCE,
                'nature_depense': DepenseExploitation.NatureDepense.BON_COMMANDE,
                'libelle': 'Travaux genie civil fondations poste',
                'devise': 'XOF', 'montant': Decimal('7800000'),
                'fournisseur': 'SOGETRA CI',
                'date_saisie': today - timedelta(days=5),
                'created_by': agent2,
            },
            {
                'centre_budgetaire': projets[2],
                'ligne_budgetaire': DepenseExploitation.LigneBudgetaire.ETUDE,
                'nature_depense': DepenseExploitation.NatureDepense.PROFORMAT,
                'libelle': 'Logiciel audit energetique EAUDIT v4 licence annuelle',
                'devise': 'USD', 'montant': Decimal('1200'),
                'fournisseur': 'ENERGY SOLUTIONS INC',
                'date_saisie': today - timedelta(days=3),
                'created_by': agent1,
            },
            {
                'centre_budgetaire': projets[2],
                'ligne_budgetaire': DepenseExploitation.LigneBudgetaire.FRAIS_MISSION,
                'nature_depense': DepenseExploitation.NatureDepense.DEMANDE_ACHAT,
                'libelle': 'Billet avion Abidjan-Korhogo A/R x2 agents',
                'devise': 'XOF', 'montant': Decimal('480000'),
                'fournisseur': 'AIR COTE D IVOIRE',
                'date_saisie': today - timedelta(days=1),
                'created_by': agent2,
            },
        ]

        for data in exploitation_data:
            DepenseExploitation.objects.create(**data)
            self.stdout.write(f"  [OK] {data['libelle'][:50]}")

        # ── Frais generaux ────────────────────────────────────────────────────
        self.stdout.write('\nCreation des frais generaux...')

        fg_data = [
            {
                'ligne_budgetaire': DepenseFraisGeneraux.LigneBudgetaire.LOYERS,
                'nature_depense': DepenseFraisGeneraux.NatureDepense.FACTURE,
                'libelle': 'Loyer bureaux mars 2026',
                'devise': 'XOF', 'montant': Decimal('850000'),
                'fournisseur': 'SCI IMMOBILIER PLATEAU',
                'date_saisie': today.replace(day=1),
                'created_by': agent1,
            },
            {
                'ligne_budgetaire': DepenseFraisGeneraux.LigneBudgetaire.CIE,
                'nature_depense': DepenseFraisGeneraux.NatureDepense.FACTURE,
                'libelle': 'Facture CIE consommation electrique fevrier 2026',
                'devise': 'XOF', 'montant': Decimal('187400'),
                'fournisseur': 'CIE',
                'date_saisie': today - timedelta(days=14),
                'created_by': agent1,
            },
            {
                'ligne_budgetaire': DepenseFraisGeneraux.LigneBudgetaire.TELEPHONE_CELLULAIRE,
                'nature_depense': DepenseFraisGeneraux.NatureDepense.FACTURE,
                'libelle': 'Abonnement Orange Business 5 lignes corporate',
                'devise': 'XOF', 'montant': Decimal('250000'),
                'fournisseur': 'ORANGE CI',
                'date_saisie': today - timedelta(days=7),
                'created_by': agent2,
            },
            {
                'ligne_budgetaire': DepenseFraisGeneraux.LigneBudgetaire.DOTATION_CARBURANT,
                'nature_depense': DepenseFraisGeneraux.NatureDepense.BON_COMMANDE,
                'libelle': 'Dotation carburant vehicules de service mars 2026',
                'devise': 'XOF', 'montant': Decimal('320000'),
                'fournisseur': 'TOTAL ENERGIES CI',
                'date_saisie': today - timedelta(days=4),
                'created_by': agent2,
            },
            {
                'ligne_budgetaire': DepenseFraisGeneraux.LigneBudgetaire.FOURNITURES_BUREAU,
                'nature_depense': DepenseFraisGeneraux.NatureDepense.DEMANDE_ACHAT,
                'libelle': 'Fournitures bureau ramettes stylos classeurs',
                'devise': 'XOF', 'montant': Decimal('95000'),
                'fournisseur': 'BUREAU DIRECT CI',
                'date_saisie': today - timedelta(days=2),
                'created_by': agent1,
            },
        ]

        for data in fg_data:
            DepenseFraisGeneraux.objects.create(**data)
            self.stdout.write(f"  [OK] {data['libelle'][:50]}")

        # ── Resume ────────────────────────────────────────────────────────────
        self.stdout.write('\n' + '-' * 55)
        self.stdout.write(self.style.SUCCESS('DONE - Donnees de demo creees avec succes !'))
        self.stdout.write('')
        self.stdout.write('  Comptes disponibles :')
        self.stdout.write(f'  Chef  : chef@atlas-energies.ci  /  {PASSWORD}')
        self.stdout.write(f'  Agent : agent1@atlas-energies.ci  /  {PASSWORD}')
        self.stdout.write(f'  Agent : agent2@atlas-energies.ci  /  {PASSWORD}')
        self.stdout.write('')
        self.stdout.write('  --> http://127.0.0.1:8000/tableau-de-bord/')
        self.stdout.write('-' * 55)
