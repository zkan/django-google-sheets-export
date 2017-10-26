from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from django.http import HttpResponseRedirect

from oauth2client.contrib import xsrfutil
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.contrib.django_util.storage import DjangoORMStorage

from .models import CredentialsModel


@login_required
def index(request):
    FLOW = OAuth2WebServerFlow(
        client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        scope='https://www.googleapis.com/auth/plus.me',
        redirect_uri='http://127.0.0.1:8000/oauth2/oauth2callback/'
    )

    storage = DjangoORMStorage(
        CredentialsModel,
        'user',
        request.user,
        'credential'
    )
    credential = storage.get()
    if credential is None or credential.invalid:
        FLOW.params['state'] = xsrfutil.generate_token(
            settings.SECRET_KEY,
            request.user
        )
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        return HttpResponse('authenticated')


@login_required
def auth_return(request):
    if not xsrfutil.validate_token(
        settings.SECRET_KEY,
        request.GET.get('state').encode('utf-8'),
        request.user
    ):
        return HttpResponseBadRequest()

    FLOW = OAuth2WebServerFlow(
        client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        scope='https://www.googleapis.com/auth/plus.me',
        redirect_uri='http://127.0.0.1:8000/oauth2/oauth2callback/'
    )

    credential = FLOW.step2_exchange(request.GET)
    storage = DjangoORMStorage(
        CredentialsModel,
        'user',
        request.user,
        'credential'
    )
    storage.put(credential)

    return HttpResponseRedirect(reverse('index'))
