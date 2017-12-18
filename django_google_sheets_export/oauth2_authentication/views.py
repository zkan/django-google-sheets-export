from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from django.http import HttpResponseRedirect

from apiclient import discovery
from oauth2client.contrib import xsrfutil
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.contrib.django_util.storage import DjangoORMStorage

from .models import CredentialsModel


@login_required
def index(request):
    FLOW = OAuth2WebServerFlow(
        client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        scope='https://www.googleapis.com/auth/spreadsheets.readonly',
        redirect_uri='http://127.0.0.1:8000/oauth2/oauth2callback/'
    )

    storage = DjangoORMStorage(
        CredentialsModel,
        'user',
        request.user,
        'credential'
    )
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        FLOW.params['state'] = xsrfutil.generate_token(
            settings.SECRET_KEY,
            request.user
        )
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        service = discovery.build('sheets', 'v4', credentials=credentials)
        # spreadsheetId = '1_5uMTTXstKUgQvz4Wfo_jw9MolxbnQTYpNrV8RI5fkI'
        spreadsheetId = '1GfI_4vM9uV4HwaVldrTaXtIlVAknFDSQ2FNdbhWI5eI'
        # range = 'Data Swarm!A:D'
        # range = 'sheets_test_range'
        range = 'Sheet1!A:A'
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheetId,
            range=range
        ).execute()
        print(result)

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
        scope='https://www.googleapis.com/auth/spreadsheets.readonly',
        redirect_uri='http://127.0.0.1:8000/oauth2/oauth2callback/'
    )

    credentials = FLOW.step2_exchange(request.GET)
    storage = DjangoORMStorage(
        CredentialsModel,
        'user',
        request.user,
        'credential'
    )
    storage.put(credentials)

    return HttpResponseRedirect(reverse('index'))
