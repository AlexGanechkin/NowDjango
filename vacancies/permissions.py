from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission

from authentication.models import User


class VacancyCreatePermission(BasePermission):
    message = 'Adding vacancies for non hr user is not allowed'

    def has_permission(self, request, view):
        # вариант проверки анонимного пользователя
        #if isinstance(request.user, AnonymousUser):
        #    return False

        if request.user.role == User.HR:
            return True
        return False
