from django.conf import settings
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response


def check_user_objects(user_model: object, email: str, username: str) -> tuple:
    """Проверяет пользователя в БД по предоставленным полям."""

    both_exists = True
    username_exists = True
    email_exists = True

    try:
        get_object_or_404(user_model, email=email)
    except Http404:
        email_exists = False

    try:
        get_object_or_404(user_model, username=username)
    except Http404:
        username_exists = False

    try:
        get_object_or_404(
            user_model, email=email, username=username
        )
    except Http404:
        both_exists = False

    return both_exists, username_exists, email_exists


def check_fields_availability(
    both_exists: bool, username_exists: bool,
    email_exists: bool, email: str, username: str
) -> tuple:
    """
    Возвращает объект ответа.
    Проверяет наличие пользователя с данными полями.
    """
    response = False
    fields_occupied = False
    email_dict = {"email": ['User with this email already registered.']}
    user_dict = {"username": ['User with this username already registered.']}
    if both_exists:
        response = {"email": email, "username": username}, status.HTTP_200_OK

    else:
        if email_exists and username_exists:
            response = {**email_dict, **user_dict}, status.HTTP_400_BAD_REQUEST
        else:
            if email_exists:
                response = email_dict, status.HTTP_400_BAD_REQUEST

            if username_exists:
                response = user_dict, status.HTTP_400_BAD_REQUEST

    if username_exists or email_exists:
        fields_occupied = True

    if not response:
        response = {"email": email, "username": username}, status.HTTP_200_OK
    return (response, fields_occupied)


def send_confirmation_code(
        user_instance: object, confirmation_code: str,
        email: str, username: str
) -> object:
    """Отправляет код подтверждения по почте."""

    subject = 'YaMDB Registration Confirmation'
    message = f'Your confirmation code is: {confirmation_code}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception:
        user_instance.delete()
        return Response(
            {'error': 'Failed to send confirmation email.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(
        {'email': email, 'username': username},
        status=status.HTTP_200_OK
    )
