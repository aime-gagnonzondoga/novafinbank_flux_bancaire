from rest_framework.permissions import BasePermission


class EstAdministrateur(BasePermission):
    """Permission réservée aux Administrateurs — RG9"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'ADMINISTRATEUR'
        )


class EstAgent(BasePermission):
    """Permission réservée aux Agents — RG2"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'AGENT'
        )


class EstClient(BasePermission):
    """Permission réservée aux Clients"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'CLIENT'
        )