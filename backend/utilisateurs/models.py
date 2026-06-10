from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from datetime import date


# ============================================
# MANAGER UTILISATEUR
# ============================================
class UtilisateurManager(BaseUserManager):

    def create_user(self, email, mot_de_passe=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(mot_de_passe)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, mot_de_passe=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMINISTRATEUR')
        return self.create_user(email, mot_de_passe, **extra_fields)


# ============================================
# MODÈLE UTILISATEUR
# ============================================
class Utilisateur(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = [
        ('CLIENT', 'Client'),
        ('AGENT', 'Agent'),
        ('ADMINISTRATEUR', 'Administrateur'),
    ]

    email         = models.EmailField(unique=True)
    role          = models.CharField(max_length=15, choices=ROLE_CHOICES)
    is_active     = models.BooleanField(default=True)
    is_staff      = models.BooleanField(default=False)
    is_superuser  = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['role']

    objects = UtilisateurManager()

    class Meta:
        db_table     = 'utilisateur'
        verbose_name = 'Utilisateur'

    def __str__(self):
        return f"{self.email} - {self.role}"


# ============================================
# MODÈLE CLIENT
# ============================================
class Client(models.Model):

    nom            = models.CharField(max_length=100)
    prenom         = models.CharField(max_length=100)
    telephone      = models.CharField(max_length=20, unique=True)
    adresse        = models.TextField(blank=True, null=True)
    date_naissance = models.DateField()
    photo_profil   = models.ImageField(upload_to='clients/photos/', blank=True, null=True)
    date_creation  = models.DateTimeField(auto_now_add=True)
    utilisateur    = models.OneToOneField(
                        Utilisateur,
                        on_delete=models.CASCADE,
                        related_name='client'
                     )

    class Meta:
        db_table     = 'client'
        verbose_name = 'Client'

    def __str__(self):
        return f"{self.nom} {self.prenom}"

    def age(self):
        today = date.today()
        age = today.year - self.date_naissance.year
        if (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day):
            age -= 1
        return age

    def clean(self):
        if self.date_naissance and self.age() < 18:
            raise ValidationError(
                "Le client doit avoir au moins 18 ans pour ouvrir un compte."
            )


# ============================================
# MODÈLE AGENT
# ============================================
class Agent(models.Model):

    matricule    = models.CharField(max_length=50, unique=True)
    nom          = models.CharField(max_length=100)
    prenom       = models.CharField(max_length=100)
    poste        = models.CharField(max_length=100, blank=True, null=True)
    photo_profil = models.ImageField(upload_to='agents/photos/', blank=True, null=True)
    utilisateur  = models.OneToOneField(
                        Utilisateur,
                        on_delete=models.CASCADE,
                        related_name='agent'
                   )

    class Meta:
        db_table     = 'agent'
        verbose_name = 'Agent'

    def __str__(self):
        return f"{self.matricule} - {self.nom} {self.prenom}"