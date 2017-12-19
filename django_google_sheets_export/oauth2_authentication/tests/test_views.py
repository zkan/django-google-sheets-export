from unittest.mock import ANY, patch

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase

from oauth2client.client import Credentials

from ..models import CredentialsModel


class OAuthIndexViewTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(
            'kan',
            'kan@pronto.com',
            'pass'
        )

    def test_oauth_view_should_require_login(self):
        response = self.client.get(reverse('index'))
        self.assertRedirects(
            response,
            '/?next=' + reverse('index'),
            status_code=302,
            target_status_code=404
        )

    def test_oauth_view_should_redirect_if_no_credential(self):
        self.client.login(username='kan', password='pass')

        with patch('oauth2_authentication.views.OAuth2WebServerFlow') as mock:
            FLOW = mock.return_value
            FLOW.step1_get_authorize_url.return_value = 'redirect_uri'

            response = self.client.get(reverse('index'))
            self.assertRedirects(
                response,
                reverse('index') + 'redirect_uri',
                status_code=302,
                target_status_code=200,
                fetch_redirect_response=False
            )

    def test_oauth_view_should_say_authenticated_if_credential_exists(self):
        self.client.login(username='kan', password='pass')

        credentials = Credentials()
        credentials.invalid = False
        CredentialsModel.objects.create(
            user=self.user,
            credential=credentials
        )

        with patch('oauth2_authentication.views.discovery'):
            response = self.client.get(reverse('index'))
            self.assertContains(response, 'authenticated', status_code=200)

    def test_oauth_view_should_get_values_in_sheet_if_credential_exists(self):
        self.client.login(username='kan', password='pass')

        credentials = Credentials()
        credentials.invalid = False
        CredentialsModel.objects.create(
            user=self.user,
            credential=credentials
        )

        with patch('oauth2_authentication.views.discovery') as mock:
            response = self.client.get(reverse('index'))
            self.assertContains(response, 'authenticated', status_code=200)

            mock.build.assert_called_once_with(
                'sheets',
                'v4',
                credentials=ANY
            )

            service = mock.build.return_value
            get = service.spreadsheets.return_value.values.return_value.get
            get.assert_called_once_with(
                spreadsheetId='1GfI_4vM9uV4HwaVldrTaXtIlVAknFDSQ2FNdbhWI5eI',
                range='Sheet1!A:A'
            )
            get.return_value.execute.assert_called_once_with()


class OAuthReturnViewTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(
            'kan',
            'kan@pronto.com',
            'pass'
        )

    def test_return_view_should_require_login(self):
        response = self.client.get(reverse('return'))
        self.assertRedirects(
            response,
            '/?next=' + reverse('return'),
            status_code=302,
            target_status_code=404
        )

    def test_return_view_should_return_bad_request_if_token_is_invalid(self):
        self.client.login(username='kan', password='pass')

        with patch('oauth2_authentication.views.xsrfutil') as mock:
            mock.validate_token.return_value = False
            response = self.client.get(reverse('return') + '?state=1234')
            self.assertEqual(response.status_code, 400)

    @patch('oauth2_authentication.views.DjangoORMStorage')
    @patch('oauth2_authentication.views.OAuth2WebServerFlow')
    @patch('oauth2_authentication.views.xsrfutil')
    def test_return_view_should_redirect_to_oauth_view_and_create_credential(
        self,
        mock_xsrfutil,
        mock_oauth2,
        mock_storage
    ):
        self.client.login(username='kan', password='pass')

        mock_xsrfutil.validate_token.return_value = True

        response = self.client.get(reverse('return') + '?state=1234')

        self.assertRedirects(
            response,
            reverse('index'),
            status_code=302,
            target_status_code=302
        )
