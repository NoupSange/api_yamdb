from django.conf import settings
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response


def check_user_objects(user_model, email, username):
    """Проверяет пользователя в БД по предоставленным полям."""

    user_both_exists = True
    user_username_exists = True
    user_email_exists = True
    try:
        get_object_or_404(user_model, email=email)
    except Http404:
        user_email_exists = False

    try:
        get_object_or_404(user_model, username=username)
    except Http404:
        user_username_exists = False

    try:
        get_object_or_404(
            user_model, email=email, username=username
        )
    except Http404:
        user_both_exists = False

    return user_both_exists, user_username_exists, user_email_exists


def check_fields_availability(
    user_both_exists, user_username_exists, user_email_exists, email, username
) -> object:
    """Возвращает объект ответа."""

    response = False
    fields_occupied = False

    if user_both_exists:
        response = Response({
                "email": email,
                "username": username},
                status=status.HTTP_200_OK
            )
    if not user_both_exists:
        if user_email_exists and user_username_exists:
            response = Response({
                "email":
                ['User with this email already registered.'],
                "username":
                ['User with this username already registered.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user_email_exists:
            response = Response({
                "email":
                ['User with this email already registered.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user_username_exists:
            response = Response({
                "username":
                ['User with this username already registered.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user_username_exists or user_email_exists:
            fields_occupied = True
    if not response:
        response = Response({
            "email": email,
            "username": username},
            status=status.HTTP_200_OK
        )
    print(response)
    return (response, fields_occupied)


def send_confirmation_code(user_instance, confirmation_code, email, username):
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
