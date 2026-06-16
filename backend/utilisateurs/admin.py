from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Client, Agent


# ============================================
# ADMIN UTILISATEUR
# ============================================
@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):

    # Colonnes affichées dans la liste
    list_display  = ['email', 'role', 'is_active', 'is_staff', 'date_creation']

    # Filtres à droite
    list_filter   = ['role', 'is_active', 'is_staff']

    # Recherche par email
    search_fields = ['email']

    # Tri par défaut
    ordering      = ['-date_creation']

    # Champs affichés dans le formulaire de modification
    fieldsets = (
        ('Informations de connexion', {
            'fields': ('email', 'password')
        }),
        ('Rôle et permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Dates', {
            'fields': ('date_creation',)
        }),
    )

    # Champs affichés dans le formulaire de création
    add_fieldsets = (
        ('Créer un utilisateur', {
            'fields': ('email', 'role', 'password1', 'password2')
        }),
    )

    # Champs non modifiables
    readonly_fields = ['date_creation']


# ============================================
# ADMIN CLIENT
# ============================================
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):

    list_display  = ['nom', 'prenom', 'telephone', 'date_creation']
    search_fields = ['nom', 'prenom', 'telephone']
    ordering      = ['-date_creation']
    readonly_fields = ['date_creation']


# ============================================
# ADMIN AGENT
# ============================================
@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):

    list_display  = ['matricule', 'nom', 'prenom', 'poste']
    search_fields = ['matricule', 'nom', 'prenom']
    ordering      = ['matricule']