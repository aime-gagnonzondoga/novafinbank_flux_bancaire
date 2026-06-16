# serializers permet de convertir les objets Python en JSON et vice versa
from rest_framework import serializers

# On importe Decimal pour les calculs financiers précis
from decimal import Decimal

# On importe le modèle Compte
from .models import Compte

# On importe Client et Agent car Compte leur est lié
from utilisateurs.models import Client, Agent

# On importe Parametre pour récupérer les valeurs configurables (RG3, RG5, RG6)
from rapports.models import Parametre


# ============================================
# SERIALIZER COMPTE
# ============================================

# CompteSerializer convertit les données Compte en JSON
# Utilisé pour l'affichage de la liste et du détail d'un compte
class CompteSerializer(serializers.ModelSerializer):

    # On affiche le nom complet du client au lieu de son id
    # SerializerMethodField permet de définir une méthode personnalisée
    client_nom = serializers.SerializerMethodField()

    # On affiche le matricule de l'agent au lieu de son id
    agent_matricule = serializers.SerializerMethodField()

    class Meta:
        # Modèle concerné
        model  = Compte

        # Champs à inclure dans le JSON retourné
        fields = [
            'id',
            'numero',
            'type',
            'statut',
            'solde',
            'date_ouverture',
            'client_nom',
            'agent_matricule',
        ]

        # Champs non modifiables via l'API
        read_only_fields = [
            'id',
            'numero',
            'solde',
            'date_ouverture',
            'client_nom',
            'agent_matricule',
        ]

    def get_client_nom(self, obj):
        """Retourne le nom complet du client propriétaire du compte"""
        return f"{obj.client.nom} {obj.client.prenom}"

    def get_agent_matricule(self, obj):
        """Retourne le matricule de l'agent qui a ouvert le compte"""
        return obj.agent.matricule


# ============================================
# SERIALIZER OUVERTURE COMPTE
# ============================================

# OuvrirCompteSerializer gère la création d'un nouveau compte
# Uniquement accessible par un Agent (RG2, RG3)
class OuvrirCompteSerializer(serializers.Serializer):

    # ID du client pour qui on ouvre le compte
    # RG1 — le client doit être enregistré avant la création d'un compte
    client_id    = serializers.IntegerField()

    # Type de compte — COURANT ou EPARGNE (RG3)
    type         = serializers.ChoiceField(choices=['COURANT', 'EPARGNE'])

    # Dépôt initial — minimum 1500 FCFA (RG3)
    depot_initial = serializers.DecimalField(max_digits=15, decimal_places=2)

    def validate_client_id(self, value):
        # RG1 — vérifier que le client existe
        if not Client.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "Ce client n'existe pas."
            )
        return value

    def validate_depot_initial(self, value):
        # RG3 — dépôt initial minimum configurable via Parametre
        try:
            # On récupère la valeur depuis la table Parametre
            depot_min = Decimal(
                Parametre.objects.get(cle='DEPOT_INITIAL_MINIMUM').valeur
            )
        except Parametre.DoesNotExist:
            # Valeur par défaut si le paramètre n'existe pas
            depot_min = Decimal('1500')

        if value < depot_min:
            raise serializers.ValidationError(
                f"Le dépôt initial minimum est de {depot_min} FCFA."
            )
        return value

    def validate(self, data):
        # RG3 — le dépôt initial doit être strictement positif
        if data['depot_initial'] <= 0:
            raise serializers.ValidationError(
                "Le dépôt initial doit être strictement positif."
            )
        return data


# ============================================
# SERIALIZER SUSPENSION COMPTE
# ============================================

# SuspendreCompteSerializer gère la suspension d'un compte
# Uniquement accessible par un Agent (RG2)
class SuspendreCompteSerializer(serializers.Serializer):

    # Motif de suspension — optionnel mais recommandé pour la traçabilité (RG2)
    motif = serializers.CharField(
                max_length=255,
                required=False,
                allow_blank=True
            )

    def validate(self, data):
        # On récupère le compte depuis le contexte
        compte = self.context.get('compte')

        # RG3 — impossible de suspendre un compte déjà suspendu
        if compte and compte.statut == 'SUSPENDU':
            raise serializers.ValidationError(
                "Ce compte est déjà suspendu."
            )
        return data


# ============================================
# SERIALIZER RÉACTIVATION COMPTE
# ============================================

# ReactiverCompteSerializer gère la réactivation d'un compte suspendu
# Uniquement accessible par un Agent (RG2)
class ReactiverCompteSerializer(serializers.Serializer):

    # Motif de réactivation — optionnel
    motif = serializers.CharField(
                max_length=255,
                required=False,
                allow_blank=True
            )

    def validate(self, data):
        # On récupère le compte depuis le contexte
        compte = self.context.get('compte')

        # RG3 — impossible de réactiver un compte déjà actif
        if compte and compte.statut == 'ACTIF':
            raise serializers.ValidationError(
                "Ce compte est déjà actif."
            )
        return data