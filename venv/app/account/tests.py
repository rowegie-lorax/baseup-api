from django.test import TestCase
from django.urls import reverse

from urllib.parse import urlencode

from oauth2_provider.tests.test_utils import TestCaseUtils
from oauth2_provider.models import AccessToken, Application
from oauth2_provider import settings
from rest_framework.test import APIClient, APIRequestFactory
from .models import User, Account
from django.utils import timezone
from django.utils.datastructures import MultiValueDict
from django.utils.http import urlencode

import datetime
import json
import base64


class ClientCredentialTest(TestCaseUtils, TestCase):
	def setUp(self):
		self.client = APIClient()

		self.test_user = User.objects.create_user("Edwin", "J", "foo@bar.com", "123456")

		self.application = Application(
			name="Test Application Client Credentials",
			redirect_uris="http://127.0.0.1:8000/api/",
			user=self.test_user,
			client_type=Application.CLIENT_PUBLIC,
			authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
			)
		self.application.save()

	def tearDown(self):
		self.test_user.delete()
		self.application.delete()

	def test_client_credentials_access_allowed(self):
		token_request_data = {'grant_type': 'client_credentials'}
		
		auth_headers = self.get_basic_auth_header(self.application.client_id, self.application.client_secret)

		response = self.client.post(reverse('oauth2_provider:token'), data=token_request_data, **auth_headers)
		self.assertEqual(response.status_code, 200)

		content = json.loads(response.content.decode("utf-8"))

		self.assertTrue('access_token' in content)
		access_token = content['access_token']

	def test_client_credentials_access_not_allowed(self):
		token_request_data = {'grant_type': 'client_credentials'}

		response = self.client.post(reverse('oauth2_provider:token'), data=token_request_data)
		self.assertEqual(response.status_code, 401)

		content = json.loads(response.content.decode("utf-8"))
		self.assertTrue('invalid_client', content['error'])

	
class AccessTokenTest(TestCaseUtils, TestCase):
	def setUp(self):
		self.client = APIClient()

		self.user = User.objects.create_user("Foo", "Bar", "foo@bar.com", "123456")
		self.user.is_active = True
		self.user.save()
		self.dev_user = User.objects.create_user("Foo", "Bar1", "dev@user.com", "123456")

		settings._SCOPES = ['read', 'write']
		settings._DEFAULT_SCOPES = ['read', 'write']

		self.application = Application(
                    name="Test Application",
                    user=self.dev_user,
                    client_type=Application.CLIENT_PUBLIC,
                    authorization_grant_type=Application.GRANT_PASSWORD,
                )
		self.application.save()

	def tearDown(self):
		self.application.delete()
		self.user.delete()
		self.dev_user.delete()

	def test_get_token(self):
	    """
	    Request an access token using Resource Owner Password Flow
	    """
	    token_request_data = {
		    'grant_type': 'password',
		    'username': 'foo@bar.com',
		    'password': '123456'
	    }

	    auth_headers = self.get_basic_auth_header(self.application.client_id, self.application.client_secret)

	    response = self.client.post(reverse('oauth2_provider:token'), data=token_request_data, **auth_headers)
	    content = json.loads(response.content.decode("utf-8"))
	    self.assertTrue('access_token' in content)
	    self.assertTrue('refresh_token' in content)


class AccountEndpointTest(TestCaseUtils, TestCase):
	def setUp(self):
		self.client = APIClient()

		self.user = User.objects.create_user("Foo", "Bar", "foo@bar.com", "123456")
		self.user.is_active = True
		self.user.save()
		self.dev_user = User.objects.create_user("Foo", "Bar1", "dev@user.com", "123456")
		self.dev_user.is_active = True
		self.dev_user.save()

		self.application = Application(
                    name="Test Application",
                    user=self.dev_user,
                    client_type=Application.CLIENT_PUBLIC,
                    authorization_grant_type=Application.GRANT_PASSWORD,
                )
		self.application.save()

		token_request_data = {
			'grant_type': 'password',
			'username': 'foo@bar.com',
			'password': '123456'
		}

		auth_headers = self.get_basic_auth_header(self.application.client_id, self.application.client_secret)

		response = self.client.post(reverse('oauth2_provider:token'), data=token_request_data, **auth_headers)
		content = json.loads(response.content.decode("utf-8"))

		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + content['access_token'])

	def tearDown(self):
		self.application.delete()
		self.user.delete()
		self.dev_user.delete()

	def test_add_new_account(self):
	    """
	    test get user information
	    """
	    response = self.client.post('/api/v1/account/', {
												    		'name': 'Test Business',
												    		'user': self.user.id,
												    		'metadata': "{'address': '24 JUMP STREET'}"
												    	})
	    self.assertEqual(response.status_code, 201)

	    content = json.loads(response.content.decode("utf-8"))
	    self.assertTrue('name' in content)
	    self.assertTrue('metadata' in content)
	    self.assertTrue('user' in content)

	def test_get_business_account_user(self):
		"""
		it should returns account info after created via POST
		"""
		response = self.client.post('/api/v1/account/', json.dumps({
    														'name': 'Test Business',
    														'user': self.user.id,
    														'metadata': {'address': '24 JUMP STREET'}
    		}))

		self.assertEqual(response.status_code, 201)

		response = self.client.get('/api/v1/users/get_user/')
		self.assertEqual(response.status_code, 200)

		content = json.loads(response.content.decode("utf-8"))
		self.assertTrue('user' in content)
		self.assertTrue('first_name' in content['user'])
		self.assertTrue('last_name' in content['user'])
		self.assertTrue('address' in content['user'])
		self.assertTrue('account' in content['user'])

		# check if account information exists
		self.assertTrue('name' in content['user']['account'])
		self.assertTrue('metadata' in content['user']['account'])

	def test_get_business_account_user(self):
		response = self.client.get('/api/v1/users/get_user/')
		self.assertEqual(response.status_code, 200)

		content = json.loads(response.content.decode("utf-8"))
		self.assertTrue('user' in content)
		self.assertTrue('first_name' in content['user'])
		self.assertTrue('last_name' in content['user'])
		self.assertTrue('address' in content['user'])
		self.assertTrue('account' in content['user'])

		self.assertEqual({}, content['user']['account'])

	def test_update_business_account(self):
		response = self.client.post('/api/v1/account/', {
    														'name': 'Test Business',
    														'user': self.user.id,
    														'metadata': "{'address': '24 JUMP STREET'}"
    		})

		self.assertEqual(response.status_code, 201)
		content = json.loads(response.content.decode("utf-8"))

		response = self.client.put('/api/v1/account/' + str(content['id']) + '/', {
    														'name': 'Test Business 1',
    														'user': self.user.id,
    														'metadata': "{'address': '24 JUMP STREET'}"
    		})

		self.assertEqual(response.status_code, 200)
		content = json.loads(response.content.decode("utf-8"))
		self.assertEqual(content['name'], 'Test Business 1')

	def test_delete_business_account(self):
		response = self.client.post('/api/v1/account/', {
    														'name': 'Test Business',
    														'user': self.user.id,
    														'metadata': "{'address': '24 JUMP STREET'}"
    		})

		self.assertEqual(response.status_code, 201)
		content = json.loads(response.content.decode("utf-8"))

		response = self.client.delete('/api/v1/account/' + str(content['id']) + '/')
		self.assertTrue(Account.objects.filter().count() == 0)

	def test_add_business_account_failed(self):
		self.client.credentials()

		response = self.client.post('/api/v1/account/', {
    														'name': 'Test Business',
    														'user': self.user.id,
    														'metadata': "{'address': '24 JUMP STREET'}"
    		})
		self.assertEqual(response.status_code, 401)

	def test_update_business_account_failed(self):
		response = self.client.post('/api/v1/account/', {
    														'name': 'Test Business',
    														'user': self.user.id,
    														'metadata': "{'address': '24 JUMP STREET'}"
    		})
		self.assertEqual(response.status_code, 201)
		content = json.loads(response.content.decode("utf-8"))

		self.client.credentials()

		response = self.client.put('/api/v1/account/' + str(content['id']) + '/', {
    														'name': 'Test Business 1',
    														'user': self.user.id,
    														'metadata': "{'address': '24 JUMP STREET'}"
    		})

		self.assertEqual(response.status_code, 401)
		content = json.loads(response.content.decode("utf-8"))
		self.assertTrue(content['detail'], 'Authentication credentials were not provided.')


class RoleEndpointTest(TestCase):
	def setUp(self):
		self.client = APIClient()

		self.user = User.objects.create_user("Foo", "Bar", "foo@bar.com", "123456")
		self.dev_user = User.objects.create_user("Foo", "Bar1", "dev@user.com", "123456")

		self.application = Application(
                    name="Test Application",
                    user=self.dev_user,
                    client_type=Application.CLIENT_PUBLIC,
                    authorization_grant_type=Application.GRANT_PASSWORD,
                )
		self.application.save()

		self.token = AccessToken(
					token="ABC123",
					user=self.user,
					expires=datetime.datetime.now() + datetime.timedelta(days=1),
					scope='read write',
					application=self.application
				)
		self.token.save()

		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.token)

	def tearDown(self):
		self.application.delete()
		self.token.delete()
		self.user.delete()
		self.dev_user.delete()