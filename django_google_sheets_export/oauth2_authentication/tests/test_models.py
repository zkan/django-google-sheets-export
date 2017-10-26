from django.contrib.auth import get_user_model
from django.test import TestCase

from oauth2client.client import Credentials

from ..models import CredentialsModel


class CredentialsModelTest(TestCase):
    def test_save_credential(self):
        User = get_user_model()
        user = User.objects.create(
            username='kan',
            password='12345',
            email='kan@pronto.com'
        )

        credentials_model = CredentialsModel()
        credentials_model.user = user
        credentials_model.credential = Credentials()
        credentials_model.save()

        credentials_model = CredentialsModel.objects.last()

        self.assertEqual(credentials_model.user, user)
        self.assertIsNotNone(credentials_model.credential)
