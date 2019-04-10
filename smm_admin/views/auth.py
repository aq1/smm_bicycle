import json

from django import http
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.core.validators import validate_email
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import get_user_model, authenticate, login

from smm_admin.models import Account


@require_http_methods(['GET'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('account'))

    return render(request, 'smm_admin/login.html')


@require_http_methods(['GET'])
def logout_view(request):
    return redirect(reverse('login'))


@require_http_methods(['POST'])
def login_post(request):
    try:
        data = json.loads(request.body)
    except (TypeError, ValueError):
        return http.HttpResponse(status=400)

    try:
        email, password, password_confirm = data['username'], data['password'], data['passwordConfirm']
    except KeyError:
        return http.HttpResponse(status=400)

    if not (email or password):
        return http.HttpResponse(status=400)

    try:
        validate_email(email)
    except ValidationError as e:
        return http.JsonResponse({'username': str(e)}, status=400)

    if password_confirm:
        if password != password_confirm:
            return http.JsonResponse({'passwordConfirm': 'Passwords do not match'}, status=400)

        try:
            user = get_user_model().objects.create_user(email, email, password)
            Account.objects.create(user=user)
        except IntegrityError:
            return http.JsonResponse({'username': 'Email is taken'}, status=400)
        
    else:
        user = authenticate(username=email, password=password)

    if not user:
        return http.HttpResponse(status=400)

    login(request, user)

    return http.JsonResponse({}, status=200)
