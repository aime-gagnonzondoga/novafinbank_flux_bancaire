from django.db import models
from django.core.exceptions import ValidationError
from utilisateurs.models import Client, Agent


# ============================================
# MODÈLE COMPTE
# ============================================
class Compte(models.Model):

    TYPE_CHOICES = [
        ('COURANT', 'Courant'),
        ('EPARGNE', 'Épargne'),
    ]

    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('SUSPENDU', 'Suspendu'),
    ]

    numero         = models.CharField(max_length=20, unique=True)
    type           = models.CharField(max_length=10, choices=TYPE_CHOICES)
    statut         = models.CharField(max_length=10, choices=STATUT_CHOICES, default='ACTIF')
    solde          = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    date_ouverture = models.DateTimeField(auto_now_add=True)
    client         = models.ForeignKey(
                        Client,
                        on_delete=models.PROTECT,
                        related_name='comptes'
                     )
    agent          = models.ForeignKey(
                        Agent,
                        on_delete=models.PROTECT,
                        related_name='comptes'
                     )

    class Meta:
        db_table     = 'compte'
        verbose_name = 'Compte'

    def __str__(self):
        return f"{self.numero} - {self.client} - {self.type}"

    def clean(self):
        if self.solde is not None and self.solde < 0:
            raise ValidationError("Le solde du compte ne peut pas être négatif.")
