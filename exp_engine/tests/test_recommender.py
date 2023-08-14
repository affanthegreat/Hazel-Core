import json
from django.test import TestCase, Client
from django.urls import reverse

from user_engine.user_management import EdenUserManagement
from leaf_engine.leaf_management import EdenLeafManagement
from leaf_engine.models import *
from user_engine.models import *
from exp_engine.models import *
from exp_engine.exp_recommender import HazelRecommendationEngine

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
             'password': 'something'
            }
        
        self.test_user_3 = {
             'user_name': "test3",
             'user_email': 'test3@example.com',
             'user_password': 'something',
             'password': 'something'
            }
        user_control_object.create_user(self.test_user_1)
        user_control_object.create_user(self.test_user_2)
        user_control_object.create_user(self.test_user_3)
        #user 1 logins and creates two leafs
        response = self.client.post(self.url, self.test_user_1,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "Login successful.")
        self.assertEqual(UserAccessToken.objects.count(), 1)
        #leaf_creation
        test_data_1 = {
             'text_content': "Salman khan goes with a car on footpath.",
             'leaf_type': 'public',
            }
        url = reverse('create_leaf')
        response = self.client.post(url, test_data_1,  content_type='application/json')
        self.leaf_id_1 = to_dict(response.content)['leaf_id']
        self.assertEqual(to_dict(response.content)['message'], 'Leaf successfully created.')
        self.assertEqual(Leaf.objects.count(),1)

        test_data_2 = {
             'text_content': "Everyone is excited for the next iphone",
             'leaf_type': 'public',
            }
        url = reverse('create_leaf')
        response = self.client.post(url, test_data_2,  content_type='application/json')
        self.leaf_id_2 = to_dict(response.content)['leaf_id']
        self.assertEqual(to_dict(response.content)['message'], 'Leaf successfully created.')
        self.assertEqual(Leaf.objects.count(),2)

        test_data_3 = {
             'text_content': "This year iphone sales are too low and stock market has seen affecting.",
             'leaf_type': 'public',
            }
        url = reverse('create_leaf')
        response = self.client.post(url, test_data_3,  content_type='application/json')
        self.leaf_id_3 = to_dict(response.content)['leaf_id']
        self.assertEqual(to_dict(response.content)['message'], 'Leaf successfully created.')
        self.assertEqual(Leaf.objects.count(),3)


        test_data_4 = {
             'text_content': "Samsung is the best! android wins!",
             'leaf_type': 'public',
            }
        url = reverse('create_leaf')
        response = self.client.post(url, test_data_4,  content_type='application/json')
        self.leaf_id_4 = to_dict(response.content)['leaf_id']
        self.assertEqual(to_dict(response.content)['message'], 'Leaf successfully created.')
        self.assertEqual(Leaf.objects.count(),4)
        
        #user 1 logouts and user 2 logins and creates a leaf
        logout_url = reverse('logout')
        logout_response = self.client.post(logout_url, self.test_user_2,  content_type='application/json')
        self.assertEqual(to_dict(logout_response.content)['message'], "Logout successful.")
        self.assertEqual(UserAccessToken.objects.count(), 0)
        #user 2 login
        response = self.client.post(self.url, self.test_user_2,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "Login successful.")
        self.assertEqual(UserAccessToken.objects.count(), 1)
        #user 2 creates a leaf
        test_data_5 = {
             'text_content': "Views in goa are so good.",
             'leaf_type': 'public',
            }
        url = reverse('create_leaf')
        response = self.client.post(url, test_data_5,  content_type='application/json')
        self.leaf_id_5 = to_dict(response.content)['leaf_id']
        self.assertEqual(to_dict(response.content)['message'], 'Leaf successfully created.')
        self.assertEqual(Leaf.objects.count(),5)

         #user 2 logouts and user 3 logins and likes user 2's leaf
        logout_url = reverse('logout')
        logout_response = self.client.post(logout_url, self.test_user_2,  content_type='application/json')
        self.assertEqual(to_dict(logout_response.content)['message'], "Logout successful.")
        self.assertEqual(UserAccessToken.objects.count(), 0)

        #user 3 login
        response = self.client.post(self.url, self.test_user_3,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "Login successful.")
        self.assertEqual(UserAccessToken.objects.count(), 1)
        like_url = reverse('like_leaf')
        test_data = {
            'leaf_id': self.leaf_id_2
        }
        response = self.client.post(like_url, test_data,  content_type='application/json')

        print("//////////////////////////////////////////////////////////")
        print(Leaf.objects.filter(leaf_id=self.leaf_id_1).values('text_content', 'leaf_topic_id', 'leaf_topic_category_id', 'topic_relevenacy_percentage',  'category_relevancy_percentage', 'exp_points'))
        print(Leaf.objects.filter(leaf_id=self.leaf_id_2).values('text_content', 'leaf_topic_id', 'leaf_topic_category_id', 'topic_relevenacy_percentage', 'category_relevancy_percentage', 'exp_points'))
        print(Leaf.objects.filter(leaf_id=self.leaf_id_3).values('text_content', 'leaf_topic_id', 'leaf_topic_category_id', 'topic_relevenacy_percentage', 'category_relevancy_percentage', 'exp_points'))
        print(Leaf.objects.filter(leaf_id=self.leaf_id_4).values('text_content', 'leaf_topic_id', 'leaf_topic_category_id', 'topic_relevenacy_percentage', 'category_relevancy_percentage', 'exp_points'))
        print(Leaf.objects.filter(leaf_id=self.leaf_id_5).values('text_content', 'leaf_topic_id', 'leaf_topic_category_id', 'topic_relevenacy_percentage', 'category_relevancy_percentage', 'exp_points'))

    def test_recommender_engine(self):
        import time 
        st = time.time()
        url = reverse('get_recommended_posts')
        test_data = {
            'page_number': 1
        }
        response = self.client.post(url, test_data,  content_type='application/json')
        r = to_dict(response.content)
        et = time.time()
        elapsed_time = et - st
        print("++++++++++++++++++++PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")
        print('Execution time:', elapsed_time, 'seconds')
        print(r['data'])
        print()
        st = time.time()
        self.assertEqual(len(r['data']), 3)