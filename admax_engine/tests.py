import json
from django.test import TestCase, Client
from django.urls import reverse

from admax_engine.models import *
from exp_engine.models import *
from leaf_engine.models import *
from user_engine.models import *

from user_engine.user_management import EdenUserManagement
from leaf_engine.leaf_management import EdenLeafManagement

user_control_object = EdenUserManagement()
leaf_control_object = EdenLeafManagement()

def to_dict(json_obj):
    return json.loads(json_obj)

class EdenAdmaxViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('login')
        self.test_user_1 = {
             'user_name': "test1",
             'user_email': 'test1@example.com',
             'user_password': 'something',
             'password': 'something'
            }
        
        user_control_object.create_user(self.test_user_1)
        self.test_user_1_id = user_control_object.get_user_id(self.test_user_1)

        response = self.client.post(self.url, self.test_user_1,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "Login successful.")
        self.assertEqual(UserAccessToken.objects.count(), 1)
    
    def test_create_advertisement_campaign(self):
        url = reverse('create_advertisement_campaign')
        test_data = {
            'user_id': self.test_user_1_id,
            'campaign_name': "Campaign 1"
        }
        response = self.client.post(url, test_data,  content_type='application/json')
        print(response.content)
        self.assertEqual(to_dict(response.content), -100) 
        self.assertEqual(Leaf.objects.count(), 0)
        self.assertEqual(AdvertisementCampaigns.objects.count(),1)
    
    def test_create_advertisement_campaign_invalid_user_id(self):
        url = reverse('create_advertisement_campaign')
        test_data = {
            'user_id': "something",
            'campaign_name': "Campaign 1"
        }
        response = self.client.post(url, test_data,  content_type='application/json')
        print(response.content)
        self.assertEqual(to_dict(response.content)['message'], "User not found.") 

    
    def test_create_advertisement_instance(self):
        url = reverse('create_advertisement_campaign')
        test_data = {
            'user_id': self.test_user_1_id,
            'campaign_name': "Campaign 1"
        }
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content), -100) 
        self.assertEqual(AdvertisementCampaigns.objects.count(),1)

        url = reverse("get_campaign_id")
        response = self.client.post(url, test_data, content_type='application/json')
        campaign_id = to_dict(response.content)
        url = reverse("create_advertisement_instance")
        test_data = {
            'user_id': self.test_user_1_id,
            'text_content': "Ad number 1",
            'target_topic_category_id' : 12,
            'advertisement_tier': 1,
            'campaign_id': campaign_id
        }
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "Advertisement is active.") 
        self.assertEqual(AdvertisementCampaigns.objects.count(),1)

    def test_create_advertisement_instance_invalid_campaign(self):
        url = reverse("create_advertisement_instance")
        test_data = {
            'user_id': self.test_user_1_id,
            'text_content': "Ad number 1",
            'target_topic_category_id' : 12,
            'advertisement_tier': 1,
            'campaign_id': "something"
        }
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "Advertisement could not be created. AdvertisementCampaigns matching query does not exist.") 
        self.assertEqual(AdvertisementCampaigns.objects.count(),0)
        
    
    def test_create_advertisement_instance_invalid_leaf_details(self):
        url = reverse('create_advertisement_campaign')
        test_data = {
            'user_id': self.test_user_1_id,
            'campaign_name': "Campaign 1"
        }
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content), -100) 
        self.assertEqual(AdvertisementCampaigns.objects.count(),1)

        url = reverse("get_campaign_id")
        response = self.client.post(url, test_data, content_type='application/json')
        campaign_id = to_dict(response.content)
        url = reverse("create_advertisement_instance")
        test_data = {
            'user_id': self.test_user_1_id,
            'text_content': "",
            'target_topic_category_id' : 12,
            'advertisement_tier': 1,
            'campaign_id': campaign_id
        }
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "Text content is empty") 
        self.assertEqual(AdvertisementCampaigns.objects.count(),1),
        self.assertEqual(Leaf.objects.count(), 0)
        

    def test_create_advertisement_instance_invalid_leaf_details(self):
        url = reverse('create_advertisement_campaign')
        test_data = {
            'user_id': self.test_user_1_id,
            'campaign_name': "Campaign 1"
        }
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content), -100) 
        self.assertEqual(AdvertisementCampaigns.objects.count(),1)

        url = reverse("get_campaign_id")
        response = self.client.post(url, test_data, content_type='application/json')
        campaign_id = to_dict(response.content)

        url = reverse("create_advertisement_instance")
        test_data = {
            'user_id': self.test_user_1_id,
            'text_content': "something",
            'target_topic_category_id' : 12,
            'advertisement_tier': 1,
            'campaign_id': campaign_id
        }
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "Advertisement is active.") 
        self.assertEqual(AdvertisementCampaigns.objects.count(),1),
        self.assertEqual(Leaf.objects.count(), 1)

        url = reverse("delete_campaign")
        test_data = {
            'campaign_id': campaign_id
        }
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content), -100) 
        self.assertEqual(AdvertisementCampaigns.objects.count(),0,)
        self.assertEqual(Advertisements.objects.count(),0)
        self.assertEqual(Leaf.objects.count(), 0)
    
    