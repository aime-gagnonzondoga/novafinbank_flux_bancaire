# serializers permet de convertir les objets Python en JSON et vice versa
from rest_framework import serializers

# On importe Decimal pour les validations financières précises
from decimal import Decimal, InvalidOperation

# On importe les modèles du module rapports
from .models import ActionAgent, LogSecurite, Parametre


# ============================================
# SERIALIZER ACTION AGENT
# ============================================
class ActionAgentSerializer(serializers.ModelSerializer):

    # Matricule de l'agent au lieu de son id
    agent_matricule = serializers.SerializerMethodField()

    # Numéro du compte au lieu de son id
    compte_numero   = serializers.SerializerMethodField()

    class Meta:
        model  = ActionAgent
        fields = [
            'id',
            'type_action',
            'date',
            'description',
            'agent_matricule',
            'compte_numero',
        ]
        # Action tracée — immuable
        read_only_fields = [
            'id',
            'type_action',
            'date',
            'description',
            'agent_matricule',
            'compte_numero',
        ]

    def get_agent_matricule(self, obj):
        """Retourne le matricule de l'agent"""
        return obj.agent.matricule

    def get_compte_numero(self, obj):
        """Retourne le numéro du compte concerné"""
        return obj.compte.numero


# ============================================
# SERIALIZER LOG SECURITE
# ============================================
class LogSecuriteSerializer(serializers.ModelSerializer):

    # Email de l'utilisateur au lieu de son id
    utilisateur_email = serializers.SerializerMethodField()

    class Meta:
        model  = LogSecurite
        fields = [
            'id',
            'action',
            'date_heure',
            'adresse_ip',
            'user_agent',
            'details',
            'utilisateur_email',
        ]
        # Log de sécurité — immuable
        read_only_fields = [
            'id',
            'action',
            'date_heure',
            'adresse_ip',
            'user_agent',
            'details',
            'utilisateur_email',
        ]

    def get_utilisateur_email(self, obj):
        """Retourne l'email de l'utilisateur
        Retourne 'Inconnu' si tentative avec email inexistant
        """
        if obj.utilisateur:
            return obj.utilisateur.email
        return 'Inconnu'


# ============================================
# SERIALIZER PARAMETRE
# ============================================
class ParametreSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Parametre
        fields = [
            'id',
            'cle',
            'valeur',
            'description',
            'updated_at',
        ]
        # cle ne change jamais — updated_at automatique
        read_only_fields = ['id', 'cle', 'updated_at']

    def validate_valeur(self, value):
        """Valide que la valeur est non vide"""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "La valeur du paramètre ne peut pas être vide."
            )
        return value.strip()


# ============================================
# SERIALIZER MODIFICATION PARAMETRE
# ============================================
class ModifierParametreSerializer(serializers.Serializer):

    # Nouvelle valeur du paramètre
    valeur = serializers.CharField(max_length=255)

    def validate_valeur(self, value):
        # Vérifier que la valeur n'est pas vide
        if not value or not value.strip():
            raise serializers.ValidationError(
                "La valeur ne peut pas être vide."
            )

        # Récupérer la clé depuis le contexte
        cle = self.context.get('cle')

        if cle == 'PLAFOND_RETRAIT_JOURNALIER':
            # Doit être un Decimal strictement positif
            try:
                val = Decimal(value)
                if val <= 0:
                    raise serializers.ValidationError(
                        "Le plafond doit être strictement positif."
                    )
            except InvalidOperation:
                raise serializers.ValidationError(
                    "Le plafond doit être un nombre valide."
                )

        elif cle == 'DEPOT_INITIAL_MINIMUM':
            # Doit être un Decimal strictement positif
            try:
                val = Decimal(value)
                if val <= 0:
                    raise serializers.ValidationError(
                        "Le dépôt initial minimum doit être strictement positif."
                    )
            except InvalidOperation:
                raise serializers.ValidationError(
                    "Le dépôt initial minimum doit être un nombre valide."
                )

        elif cle == 'FRAIS_TRANSFERT_FIXE':
            # Doit être un Decimal >= 0
            try:
                val = Decimal(value)
                if val < 0:
                    raise serializers.ValidationError(
                        "Les frais fixes ne peuvent pas être négatifs."
                    )
            except InvalidOperation:
                raise serializers.ValidationError(
                    "Les frais fixes doivent être un nombre valide."
                )

        elif cle == 'TAUX_FRAIS_TRANSFERT':
            # Doit être un Decimal entre 0 et 1
            try:
                val = Decimal(value)
                if val < 0 or val > 1:
                    raise serializers.ValidationError(
                        "Le taux doit être compris entre 0 et 1 "
                        "(ex: 0.003 pour 0.3%)."
                    )
            except InvalidOperation:
                raise serializers.ValidationError(
                    "Le taux doit être un nombre valide."
                )

        else:
            # Clé inconnue — on accepte sans validation spécifique
            # Les clés sont fixes donc ce cas ne devrait pas arriver
            pass

        return value.strip()