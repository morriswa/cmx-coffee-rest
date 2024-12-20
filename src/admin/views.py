"""
    Admin-related django views (http request actions) go here
"""
import logging

from django.core import mail
from django.conf import settings

from rest_framework.request import Request
from rest_framework.response import Response

from app.decorators import admin_view
from app.exceptions import BadRequestException

import admin.daos as admin_dao


@admin_view(['GET'])
def get_pending_vendor_applications(request: Request) -> Response:
    apps = admin_dao.get_pending_vendor_applications()
    return Response(status=200, data=[app.json() for app in apps])

@admin_view(['PUT'])
def process_pending_vendor_application(request: Request, application_id: int) -> Response:
    requested_action = request.query_params.get('action')
    match requested_action:
        case 'approve':
            admin_dao.approve_vendor_application(request.user.user_id, application_id)
            return Response(status=204)
        case 'reject':
            admin_dao.reject_vendor_application(application_id)
            return Response(status=204)
        case _:
            raise BadRequestException('invalid action')

@admin_view(['GET'])
def get_all_vendors(request: Request) -> Response:
    vendors = admin_dao.get_all_vendors()
    return Response(status=200, data=[vendor.json() for vendor in vendors])

@admin_view(['POST'])
def send_subscribers_email(request: Request):
    recipients = admin_dao.get_all_newsletter_subscriber_emails()
    Subject = "K&M Coffee Co. Newsletter"

    #Reads the file that holds the newsletter template and assigns it to variable used later.
    with open(settings.BASE_DIR / 'app/email/app-email-template.html', "r") as file:
        message = file.read()

    mail.send_mail(
        subject=Subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=recipients,
        html_message=message
    )
    return Response(status=204)

@admin_view(['GET'])
def get_all_newsletter_subscriber_emails(request: Request) -> Response:
    emails = admin_dao.get_all_newsletter_subscriber_emails()
    return Response(status=200, data=[email.json() for email in emails])
