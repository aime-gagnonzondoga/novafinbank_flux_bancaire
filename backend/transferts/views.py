# APIView permet de créer des vues basées sur des classes
from rest_framework.views import APIView

# Response permet de retourner des réponses JSON
from rest_framework.response import Response

# status contient les codes HTTP
from rest_framework import status

# IsAuthenticated — session active requise (RG0)
from rest_framework.permissions import IsAuthenticated

# transaction.atomic() — garantit que toutes les opérations réussissent
# ou qu'aucune n'est appliquée — critique pour les opérations financières
from django.db import transaction as db_transaction

# Q permet de faire des requêtes avec conditions OR
from django.db.models import Q

# On importe le modèle Transfert
from .models import Transfert

# On importe les serializers
from .serializers import (
    TransfertSerializer,
    EffectuerTransfertSerializer,
)

# On importe Transaction — un transfert génère 2 transactions (RG6)
from transactions.models import Transaction

# On importe Client pour la vérification de propriétaire
from utilisateurs.models import Client

# On importe les permissions
from utilisateurs.permissions import EstAdministrateur, EstClient


# ============================================
# VUE EFFECTUER TRANSFERT
# ============================================

# EffectuerTransfertView gère la création d'un transfert
# EstClient — uniquement accessible par un Client (RG6)
class EffectuerTransfertView(APIView):

    permission_classes = [EstClient]

    def post(self, request):
        """Effectuer un transfert entre deux comptes"""

        serializer = EffectuerTransfertSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.validated_data

            compte_source = validated_data['compte_source']
            compte_dest   = validated_data['compte_dest']
            montant       = validated_data['montant']
            frais         = validated_data['frais']

            # transaction.atomic() — tout ou rien
            # Si une opération échoue → tout est annulé
            # Critique pour éviter les pertes d'argent (RG6)
            with db_transaction.atomic():

                # Débiter le compte source — montant + frais (RG6)
                compte_source.solde -= (montant + frais)
                compte_source.save()

                # Créditer le compte destination — montant uniquement (RG6)
                compte_dest.solde += montant
                compte_dest.save()

                # Créer le transfert — RG6
                transfert = Transfert.objects.create(
                    montant       = montant,
                    frais         = frais,
                    statut        = 'SUCCES',
                    compte_source = compte_source,
                    compte_dest   = compte_dest,
                )

                # Créer transaction TRANSFERT_DEBIT — RG6, RG7
                Transaction.objects.create(
                    type      = 'TRANSFERT_DEBIT',
                    montant   = montant,
                    frais     = frais,
                    statut    = 'SUCCES',
                    compte    = compte_source,
                    transfert = transfert,
                )

                # Créer transaction TRANSFERT_CREDIT — RG6, RG7
                # frais = 0 sur le crédit — RG6
                Transaction.objects.create(
                    type      = 'TRANSFERT_CREDIT',
                    montant   = montant,
                    frais     = 0,
                    statut    = 'SUCCES',
                    compte    = compte_dest,
                    transfert = transfert,
                )

            return Response(
                {
                    'message'              : 'Transfert effectué avec succès.',
                    'transfert'            : TransfertSerializer(transfert).data,
                    'frais'                : str(frais),
                    'nouveau_solde_source' : str(compte_source.solde),
                },
                status=status.HTTP_201_CREATED
            )


# ============================================
# VUE LISTE TRANSFERTS CLIENT
# ============================================

# ListeTransfertsClientView retourne tous les transferts du client connecté
# IsAuthenticated — RG0
class ListeTransfertsClientView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retourner tous les transferts du client connecté"""

        # Client.DoesNotExist — spécifique et précis
        try:
            client = request.user.client
        except Client.DoesNotExist:
            return Response(
                {'error': 'Profil client introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Récupérer tous les comptes du client
        comptes = client.comptes.all()

        # Q(source) | Q(dest) — transferts émis ET reçus
        transferts = Transfert.objects.filter(
            Q(compte_source__in=comptes) | Q(compte_dest__in=comptes)
        ).select_related(
            'compte_source', 'compte_dest'
        ).order_by('-date_heure')

        serializer = TransfertSerializer(transferts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================
# VUE DÉTAIL TRANSFERT
# ============================================

# DetailTransfertView retourne le détail d'un transfert
# IsAuthenticated — RG0
class DetailTransfertView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Retourner le détail d'un transfert"""

        try:
            transfert = Transfert.objects.select_related(
                'compte_source', 'compte_dest'
            ).get(pk=pk)
        except Transfert.DoesNotExist:
            return Response(
                {'error': 'Transfert introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Un client ne peut voir que ses propres transferts
        if request.user.role == 'CLIENT':
            try:
                client = request.user.client
                # values_list → comparaison par IDs — efficace et correct
                comptes_ids = client.comptes.values_list('id', flat=True)
                if (transfert.compte_source_id not in comptes_ids and
                        transfert.compte_dest_id not in comptes_ids):
                    return Response(
                        {'error': 'Accès refusé. Ce transfert ne vous appartient pas.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Client.DoesNotExist:
                return Response(
                    {'error': 'Profil client introuvable.'},
                    status=status.HTTP_404_NOT_FOUND
                )

        serializer = TransfertSerializer(transfert)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================
# VUE LISTE TOUS LES TRANSFERTS
# ============================================

# ListeTousTransfertsView — Admin uniquement — RG9
class ListeTousTransfertsView(APIView):

    permission_classes = [EstAdministrateur]

    def get(self, request):
        """Retourner tous les transferts — réservé à l'Administrateur"""

        transferts = Transfert.objects.select_related(
            'compte_source', 'compte_dest'
        ).all().order_by('-date_heure')

        serializer = TransfertSerializer(transferts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)