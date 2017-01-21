from httplib2 import Http

from django.conf import settings
from django.utils.crypto import get_random_string
from apiclient.errors import HttpError
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from core.models import Event


GAPPS_JSON_CREDENTIALS = {
  "type": "service_account",
  "project_id": "djangogirls-website",
  "private_key_id": settings.GAPPS_PRIVATE_KEY_ID,
  "private_key": settings.GAPPS_PRIVATE_KEY,
  "client_email": "django-girls-website@djangogirls-website.iam.gserviceaccount.com",
  "client_id": "114585708723701029855",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/django-girls-website%40djangogirls-website.iam.gserviceaccount.com"
}


def get_gapps_client():
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        GAPPS_JSON_CREDENTIALS,
        scopes=settings.GAPPS_ADMIN_SDK_SCOPES
    )

    delegated_credentials = credentials.create_delegated('hello@djangogirls.org')
    http_auth = delegated_credentials.authorize(Http())

    return build('admin', 'directory_v1', http=http_auth)


def make_email(slug):
    """Get the email address for the given slug"""
    return '%s@djangogirls.org' % slug


def create_gmail_account(event):
    """
    Create a new account
    """
    email = event.email
    password = get_random_string(length=10)
    get_gapps_client().users().insert(body={
        "primaryEmail": email,
        "name": {
            "fullName": event.name,
            "givenName": "Django Girls",
            "familyName": event.city,
        },
        "password": password,
    }).execute()

    return (email, password)


def migrate_gmail_account(slug):
    """
    Change the name of an account
    """
    old_email = make_email(slug)
    old_event = Event.objects.filter(email=old_email).order_by('-id').first()
    new_email = make_email(slug+str(old_event.date.month)+str(old_event.date.year))
    service = get_gapps_client()

    service.users().patch(
        userKey=old_email,
        body={
            "primaryEmail": new_email,
        },
    ).execute()

    # The old email address is kept as an alias to the new one, but we don't want this.
    service.users().aliases().delete(userKey=new_email, alias=old_email).execute()

    old_event.email = new_email
    old_event.save()


def get_gmail_account(slug):
    """
    Return the details of the given account - just pass in the slug
    e.g. get_account('testcity')
    """
    service = get_gapps_client()

    try:
        return service.users().get(userKey=make_email(slug)).execute()
    except HttpError:
        return None
