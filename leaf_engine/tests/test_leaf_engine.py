import json
from django.test import TestCase, Client
from django.urls import reverse

from user_engine.user_management import EdenUserManagement
from leaf_engine.leaf_management import EdenLeafManagement
from leaf_engine.models import *
from user_engine.models import *

def to_dict(json_obj):
    return json.loads(json_obj)

user_control_object = EdenUserManagement()
leaf_control_object = EdenLeafManagement()

class EdenUserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('login')
        self.test_user_1 = {
             'user_name': "test1",
             'user_email': 'test1@example.com',
             'user_password': 'something',
             'password': 'something'
            }
        self.test_user_2 = {
             'user_name': "test2",
             'user_email': 'test2@example.com',
             'user_password': 'something',
            }
        
        user_control_object.create_user(self.test_user_1)
        user_control_object.create_user(self.test_user_2)

        response = self.client.post(self.url, self.test_user_1,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "Login successful.")
        self.assertEqual(UserAccessToken.objects.count(), 1)
    

    def test_create_leaf(self):
        test_data = {
             'text_content': "Public Leaf 1",
             'leaf_type': 'public',
            }
        url = reverse('create_leaf')
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], 'Leaf successfully created.')
        self.assertEqual(Leaf.objects.count(),1)

    def test_create_leaf_invalid_fields(self):
        test_data = {
             'text_content': "Public Leaf 1",
             'leaf': 'public',
            }
        url = reverse('create_leaf')
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], 'Valid fields not found in request body')
    
    def test_invalid_leaf_type(self):
        test_data = {
            'text_content': "public leaf",
            'leaf_type': 'personal'
        }
        url = reverse('create_leaf')
        response = self.client.post(url, test_data,  content_type='application/json')   
        self.assertEqual(to_dict(response.content)['message'], 'Invalid leaf type')

    def test_delete_leaf(self):
        test_data = {
             'text_content': "Public Leaf 1",
             'leaf_type': 'public',
            }
        url = reverse('create_leaf')
        delete_url = reverse('delete_leaf')
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], 'Leaf successfully created.')
        self.assertEqual(Leaf.objects.count(),1)
        deletion_data = {
            'leaf_id': to_dict(response.content)['leaf_id']
        }
        delete_response = self.client.post(delete_url, deletion_data,  content_type='application/json')
        self.assertEqual(to_dict(delete_response.content)['message'], '-100')
    
    def test_delete_non_existing_leaf(self):
        delete_url = reverse('delete_leaf')
        deletion_data = {
            'leaf_id': "223134141313"
        }
        delete_response = self.client.post(delete_url, deletion_data,  content_type='application/json')
        self.assertEqual(to_dict(delete_response.content)['message'], 'Leaf not found.')
    
    def test_delete_leaf_invalid_field(self):
        delete_url = reverse('delete_leaf')
        deletion_data = {
            'leaf': "223134141313"
        }
        delete_response = self.client.post(delete_url, deletion_data,  content_type='application/json')
        self.assertEqual(to_dict(delete_response.content)['message'], "Valid fields not found in request body")
    
    def test_get_user_public_leaves(self):
        test_data = {
             'text_content': "Public Leaf 1",
             'leaf_type': 'public',
            }
        url = reverse('create_leaf')
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], 'Leaf successfully created.')
        self.assertEqual(Leaf.objects.count(),1)
        url = reverse('get_user_public_leaves')
        response = self.client.get(f'{url}?page_number=1')
        self.assertEqual(len(to_dict(response.content)['data']),1)
    
    def test_get_user_private_leaves(self):
        test_data = {
             'text_content': "Public Leaf 1",
             'leaf_type': 'private',
            }
        url = reverse('create_leaf')
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], 'Leaf successfully created.')
        self.assertEqual(Leaf.objects.count(),1)
        url = reverse('get_user_private_leaves')
        response = self.client.get(f'{url}?page_number=1')
        self.assertEqual(len(to_dict(response.content)['data']),1)