# serializers permet de convertir les objets Python en JSON et vice versa
from rest_framework import serializers
from datetime import date

# On importe les modèles à sérialiser
from .models import Utilisateur, Client, Agent


# ============================================
# SERIALIZER UTILISATEUR
# ============================================
class UtilisateurSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Utilisateur
        fields = [
            'id',
            'email',
            'role',
            'is_active',
            'date_creation'
        ]
        read_only_fields = ['id', 'date_creation']


# ============================================
# SERIALIZER INSCRIPTION CLIENT
# ============================================
class ClientInscriptionSerializer(serializers.ModelSerializer):

    # Email — write_only car géré dans Utilisateur pas dans Client
    email          = serializers.EmailField(write_only=True)

    # Mot de passe — write_only pour la sécurité
    mot_de_passe   = serializers.CharField(write_only=True)

    # Confirmation mot de passe
    mot_de_passe2  = serializers.CharField(write_only=True)

    class Meta:
        model  = Client
        fields = [
            'nom',
            'prenom',
            'email',
            'telephone',
            'adresse',
            'date_naissance',
            'mot_de_passe',
            'mot_de_passe2',
        ]

    def validate_email(self, value):
        # RG1 — email unique
        if Utilisateur.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Cet email est déjà utilisé."
            )
        return value

    def validate_telephone(self, value):
        # RG1 — téléphone unique
        if Client.objects.filter(telephone=value).exists():
            raise serializers.ValidationError(
                "Ce numéro de téléphone est déjà utilisé."
            )
        return value

    def validate_date_naissance(self, value):
        # RG1 — âge minimum 18 ans
        today = date.today()
        age = today.year - value.year
        if (today.month, today.day) < (value.month, value.day):
            age -= 1
        if age < 18:
            raise serializers.ValidationError(
                "Le client doit avoir au moins 18 ans."
            )
        return value

    def validate(self, data):
        # Vérification que les deux mots de passe sont identiques
        if data['mot_de_passe'] != data['mot_de_passe2']:
            raise serializers.ValidationError(
                "Les deux mots de passe ne correspondent pas."
            )
        return data

    def create(self, validated_data):
        # On retire les champs qui ne sont pas dans Client
        validated_data.pop('mot_de_passe2')
        mot_de_passe = validated_data.pop('mot_de_passe')
        email        = validated_data.pop('email')

        # Création de l'utilisateur de base avec rôle CLIENT
        utilisateur = Utilisateur.objects.create_user(
            email=email,
            mot_de_passe=mot_de_passe,
            role='CLIENT'
        )

        # Création du profil client lié à cet utilisateur
        client = Client.objects.create(
            utilisateur=utilisateur,
            **validated_data
        )

        return client


# ============================================
# SERIALIZER CLIENT
# ============================================
class ClientSerializer(serializers.ModelSerializer):

    # Infos utilisateur imbriquées — read_only
    utilisateur = UtilisateurSerializer(read_only=True)

    class Meta:
        model  = Client
        fields = [
            'id',
            'nom',
            'prenom',
            'telephone',
            'adresse',
            'date_naissance',
            'photo_profil',
            'date_creation',
            'utilisateur',
        ]
        read_only_fields = ['id', 'date_creation', 'utilisateur']


# ============================================
# SERIALIZER AGENT
# ============================================
class AgentSerializer(serializers.ModelSerializer):

    # Infos utilisateur imbriquées — read_only
    utilisateur = UtilisateurSerializer(read_only=True)

    class Meta:
        model  = Agent
        fields = [
            'id',
            'matricule',
            'nom',
            'prenom',
            'poste',
            'photo_profil',
            'utilisateur',
        ]
        read_only_fields = ['id', 'matricule', 'utilisateur']


# ============================================
# SERIALIZER CRÉATION AGENT
# ============================================
class AgentCreationSerializer(serializers.ModelSerializer):

    # Email — write_only car géré dans Utilisateur
    email        = serializers.EmailField(write_only=True)

    # Mot de passe — write_only pour la sécurité
    mot_de_passe = serializers.CharField(write_only=True)

    class Meta:
        model  = Agent
        fields = [
            'matricule',
            'nom',
            'prenom',
            'poste',
            'email',
            'mot_de_passe',
        ]

    def validate_email(self, value):
        # Email unique — RG0
        if Utilisateur.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Cet email est déjà utilisé."
            )
        return value

    def validate_matricule(self, value):
        # Matricule unique — RG2
        if Agent.objects.filter(matricule=value).exists():
            raise serializers.ValidationError(
                "Ce matricule est déjà utilisé."
            )
        return value

    def create(self, validated_data):
        email        = validated_data.pop('email')
        mot_de_passe = validated_data.pop('mot_de_passe')

        # Création utilisateur avec rôle AGENT
        utilisateur = Utilisateur.objects.create_user(
            email=email,
            mot_de_passe=mot_de_passe,
            role='AGENT'
        )

        # Création profil agent
        agent = Agent.objects.create(
            utilisateur=utilisateur,
            **validated_data
        )

        return agent