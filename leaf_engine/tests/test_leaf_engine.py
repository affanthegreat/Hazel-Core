import json
from django.test import TestCase, Client
from django.urls import reverse

from user_engine.user_management import EdenUserManagement
from leaf_engine.leaf_management import EdenLeafManagement
from leaf_engine.models import *
from user_engine.models import *
from exp_engine.models import *

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

class EdenLeafFunctionalityTests(TestCase):
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
        
        user_control_object.create_user(self.test_user_1)
        user_control_object.create_user(self.test_user_2)
        self.test_user_1_id = user_control_object.get_user_id(self.test_user_1)
        self.test_user_2_id = user_control_object.get_user_id(self.test_user_2)

        response = self.client.post(self.url, self.test_user_1,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "Login successful.")
        self.assertEqual(UserAccessToken.objects.count(), 1)
        #2 Users, User 1 logged in.
        follow_url = reverse('follow')
        test_data = {'follower':self.test_user_1_id, 'follows':self.test_user_2_id}
        response = self.client.post(follow_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], 'test1 added as follower to test2')
        self.assertEqual(UserFollowing.objects.count(), 1)
        #User 1 follows user 2
        test_data = {
             'text_content': "Public Leaf 1",
             'leaf_type': 'public',
            }
        logout_url = reverse('logout')
        logout_response = self.client.post(logout_url, self.test_user_1,  content_type='application/json')
        self.assertEqual(to_dict(logout_response.content)['message'], "Logout successful.")
        self.assertEqual(UserAccessToken.objects.count(), 0)
        #User 1 Logout and User 2 Login
        login_response = self.client.post(reverse('login'), self.test_user_2,  content_type='application/json')
        self.assertEqual(to_dict(login_response.content)['message'], "Login successful.")
        self.assertEqual(UserAccessToken.objects.count(), 1)
        #User 2 Creates a new leaf
        url = reverse('create_leaf')
        response = self.client.post(url, test_data,  content_type='application/json')
        self.leaf_id = to_dict(response.content)['leaf_id']
        self.assertEqual(to_dict(response.content)['message'], 'Leaf successfully created.')
        self.assertEqual(Leaf.objects.count(),1)
        #User 2 logouts and user 1 login
        logout_url = reverse('logout')
        logout_response = self.client.post(logout_url, self.test_user_2,  content_type='application/json')
        self.assertEqual(to_dict(logout_response.content)['message'], "Logout successful.")
        self.assertEqual(UserAccessToken.objects.count(), 0)

        login_response = self.client.post(reverse('login'), self.test_user_1,  content_type='application/json')
        self.assertEqual(to_dict(login_response.content)['message'], "Login successful.")
        self.assertEqual(UserAccessToken.objects.count(), 1)
        
    def test_like_leaf(self):
        like_url = reverse('like_leaf')
        test_data = {
            'leaf_id': self.leaf_id
        }
        response = self.client.post(like_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content), -100)
        self.assertEqual(LeafLikes.objects.count(), 1)
        self.assertEqual(LeafInteraction.objects.count(), 1)
        self.assertEqual(UserTopicRelations.objects.count(), 1)
        self.assertEqual(UserLeafPreferences.objects.count(), 1)
    
    def test_like_leaf_non_existant(self):
        like_url = reverse('like_leaf')
        test_data = {
            'leaf_id': "DOES NOT EXISTS"
        }
        response = self.client.post(like_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content), -103)
        self.assertEqual(LeafLikes.objects.count(), 0)
        self.assertEqual(LeafInteraction.objects.count(), 0)
        self.assertEqual(UserTopicRelations.objects.count(), 0)
        self.assertEqual(UserLeafPreferences.objects.count(), 0)
    
    def test_dislike_leaf(self):
        dislike_url = reverse('dislike_leaf')
        test_data = {
            'leaf_id': self.leaf_id
        }
        response = self.client.post(dislike_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content), -100)
        self.assertEqual(LeafDisLikes.objects.count(), 1)
        self.assertEqual(LeafInteraction.objects.count(), 1)
        self.assertEqual(UserTopicRelations.objects.count(), 1)
        self.assertEqual(UserLeafPreferences.objects.count(), 1)
    
    def test_dislike_leaf_non_existant(self):
        dislike_url = reverse('dislike_leaf')
        test_data = {
            'leaf_id': "THIS DOES NOT EXISTS"
        }
        response = self.client.post(dislike_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content), -103)
        self.assertEqual(LeafDisLikes.objects.count(), 0)
        self.assertEqual(LeafInteraction.objects.count(), 0)
        self.assertEqual(UserTopicRelations.objects.count(), 0)
        self.assertEqual(UserLeafPreferences.objects.count(), 0)
    
    def test_remove_like(self):
        like_url = reverse('like_leaf')
        test_data = {
            'leaf_id': self.leaf_id
        }
        self.client.post(like_url, test_data,  content_type='application/json')
        remove_like_url = reverse('remove_like')
        test_data = {
            'leaf_id': self.leaf_id
        }
        response = self.client.post(remove_like_url, test_data,  content_type='application/json')

        self.assertEqual(to_dict(response.content), -100)
        self.assertEqual(LeafLikes.objects.count(), 0)
        self.assertEqual(LeafInteraction.objects.count(), 1)
        self.assertEqual(UserTopicRelations.objects.count(), 1)
        self.assertEqual(UserLeafPreferences.objects.count(), 1)
    
    def test_remove_dislike(self):
        dislike_url = reverse('dislike_leaf')
        test_data = {
            'leaf_id': self.leaf_id
        }
        response = self.client.post(dislike_url, test_data,  content_type='application/json')
        remove_like_url = reverse('remove_dislike')
        test_data = {
            'leaf_id': self.leaf_id
        }
       
        response = self.client.post(remove_like_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content), -100)
        self.assertEqual(LeafLikes.objects.count(), 0)
        self.assertEqual(LeafInteraction.objects.count(), 1)
        self.assertEqual(UserTopicRelations.objects.count(), 1)
        self.assertEqual(UserLeafPreferences.objects.count(), 1)

    def test_get_total_likes(self):
        like_url = reverse('like_leaf')
        test_data = {
            'leaf_id': self.leaf_id
        }
        response = self.client.post(like_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content), -100)
        self.assertEqual(LeafLikes.objects.count(), 1)
        self.assertEqual(LeafInteraction.objects.count(), 1)
        self.assertEqual(UserTopicRelations.objects.count(), 1)
        self.assertEqual(UserLeafPreferences.objects.count(), 1)
        url = reverse('get_all_likes')
        response = self.client.get(f'{url}?page_number=1&leaf_id={self.leaf_id}')
        self.assertEqual(len(to_dict(response.content)['data']),1)
    
    def test_get_total_likes_non_existant_leaf(self):
        like_url = reverse('like_leaf')
        test_data = {
            'leaf_id': "Non Existing Leaf"
        }
        response = self.client.post(like_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content), -103)
        self.assertEqual(LeafLikes.objects.count(), 0)
        self.assertEqual(LeafInteraction.objects.count(), 0)
        self.assertEqual(UserTopicRelations.objects.count(), 0)
        self.assertEqual(UserLeafPreferences.objects.count(), 0)
        url = reverse('get_all_likes')
        response = self.client.get(f'{url}?page_number=1&leaf_id={self.leaf_id}')
        self.assertEqual(len(to_dict(response.content)['data']),0)

    def test_get_total_comments(self):
        comment_url = reverse('add_comment')
        test_data = {
            'leaf_id': self.leaf_id,
            'comment_string': "Test comment 1"
        }
        response = self.client.post(comment_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], -100)
        self.assertEqual(LeafComments.objects.count(), 1)
        self.assertEqual(LeafInteraction.objects.count(), 1)
        self.assertEqual(UserTopicRelations.objects.count(), 1)
        self.assertEqual(UserLeafPreferences.objects.count(), 1)
        url = reverse('get_all_comments')
        response = self.client.get(f'{url}?page_number=1&leaf_id={self.leaf_id}')
        self.assertEqual(len(to_dict(response.content)['data']),1)
    
    def test_add_comment(self):
        comment_url = reverse('add_comment')
        test_data = {
            'leaf_id': self.leaf_id,
            'comment_string': "Test comment 1"
        }
        response = self.client.post(comment_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], -100)
        self.assertEqual(LeafComments.objects.count(), 1)
        self.assertEqual(LeafInteraction.objects.count(), 1)
        self.assertEqual(UserTopicRelations.objects.count(), 1)
        self.assertEqual(UserLeafPreferences.objects.count(), 1)

    def test_add_comment_non_existant_leaf(self):
        comment_url = reverse('add_comment')
        test_data = {
            'leaf_id': "THIS NOT EXISTS",
            'comment_string': "Test comment 1"
        }
        response = self.client.post(comment_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], -103)
        self.assertEqual(LeafComments.objects.count(), 0)
        self.assertEqual(LeafInteraction.objects.count(), 0)
        self.assertEqual(UserTopicRelations.objects.count(), 0)
        self.assertEqual(UserLeafPreferences.objects.count(), 0)
    
    def test_add_comment_empty_string(self):
        comment_url = reverse('add_comment')
        test_data = {
            'leaf_id': "THIS NOT EXISTS",
            'comment_string': " "
        }
        response = self.client.post(comment_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], -103)
        self.assertEqual(LeafComments.objects.count(), 0)
        self.assertEqual(LeafInteraction.objects.count(), 0)
        self.assertEqual(UserTopicRelations.objects.count(), 0)
        self.assertEqual(UserLeafPreferences.objects.count(), 0)
    
    
    def test_remove_comment(self):
        comment_url = reverse('add_comment')
        test_data = {
            'leaf_id': self.leaf_id,
            'comment_string': "Test comment 1"
        }
        response = self.client.post(comment_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], -100)
        self.assertEqual(LeafComments.objects.count(), 1)
        self.assertEqual(LeafInteraction.objects.count(), 1)
        self.assertEqual(UserTopicRelations.objects.count(), 1)
        self.assertEqual(UserLeafPreferences.objects.count(), 1)
        comment_url = reverse('remove_comment')
        test_data = {
            'leaf_id': self.leaf_id,
        }
        response = self.client.post(comment_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content), -100)
        self.assertEqual(LeafComments.objects.count(), 0)
        self.assertEqual(LeafInteraction.objects.count(), 1)
        self.assertEqual(UserTopicRelations.objects.count(), 2)
        self.assertEqual(UserLeafPreferences.objects.count(), 1)
    
    def test_remove_comment_non_existant_leaf(self):
        comment_url = reverse('add_comment')
        test_data = {
            'leaf_id': self.leaf_id,
            'comment_string': "Test comment 1"
        }
        response = self.client.post(comment_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], -100)
        self.assertEqual(LeafComments.objects.count(), 1)
        self.assertEqual(LeafInteraction.objects.count(), 1)
        self.assertEqual(UserTopicRelations.objects.count(), 1)
        self.assertEqual(UserLeafPreferences.objects.count(), 1)
        comment_url = reverse('remove_comment')
        test_data = {
            'leaf_id': "NON EXISTANT LEAF",
        }
        response = self.client.post(comment_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content), -103)
        self.assertEqual(LeafComments.objects.count(), 1)
        self.assertEqual(LeafInteraction.objects.count(), 1)
        self.assertEqual(UserTopicRelations.objects.count(), 1)
        self.assertEqual(UserLeafPreferences.objects.count(), 1)
    
    def test_add_sub_comment(self):
        comment_url = reverse('add_comment')
        test_data = {
            'leaf_id': self.leaf_id,
            'comment_string': "Test comment 1"
        }
        response = self.client.post(comment_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], -100)
        comment_url = reverse('add_sub_comment')
        test_data = {
            'leaf_id': self.leaf_id,
            'comment_string': "Test comment 1",
            'parent_comment_id': LeafComments.objects.first().comment_id
        }
        response = self.client.post(comment_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content), -100)
        self.assertEqual(LeafComments.objects.count(), 2)
        self.assertEqual(LeafInteraction.objects.count(), 2)
        self.assertEqual(UserTopicRelations.objects.count(), 2)
        self.assertEqual(UserLeafPreferences.objects.count(), 2)
    
    def test_add_sub_comment_invalid_parent_comment_id(self):
        comment_url = reverse('add_sub_comment')
        test_data = {
            'leaf_id': self.leaf_id,
            'comment_string': "Test comment 1",
            'parent_comment_id': "NON EXISTANT"
        }
        response = self.client.post(comment_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content), -103)
        self.assertEqual(LeafComments.objects.count(), 1)
        self.assertEqual(LeafInteraction.objects.count(), 1)
        self.assertEqual(UserTopicRelations.objects.count(), 1)
        self.assertEqual(UserLeafPreferences.objects.count(), 1)
    
    def test_add_sub_comment_invalid_leaf_id(self):
        comment_url = reverse('add_sub_comment')
        test_data = {
            'leaf_id': "NON EXISTANT",
            'comment_string': "Test comment 1",
            'parent_comment_id': "NON EXISTANT"
        }
        response = self.client.post(comment_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'],"Valid fields not found in request body")
        self.assertEqual(LeafComments.objects.count(), 0)
        self.assertEqual(LeafInteraction.objects.count(), 0)
        self.assertEqual(UserTopicRelations.objects.count(), 0)
        self.assertEqual(UserLeafPreferences.objects.count(), 0)
    

    def test_add_view(self):
        comment_url = reverse('add_view')
        test_data = {
            'leaf_id': self.leaf_id,
        }
        response = self.client.post(comment_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content), -100)
        self.assertEqual(LeafViewedBy.objects.count(), 1)
        self.assertEqual(LeafInteraction.objects.count(), 1)
        self.assertEqual(UserTopicRelations.objects.count(), 1)
        self.assertEqual(UserLeafPreferences.objects.count(), 1)
    
    def test_add_view_non_existant_leaf(self):
        comment_url = reverse('add_view')
        test_data = {
            'leaf_id': "NON EXISTANT LEAF",
        }
        response = self.client.post(comment_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content), -124)
        self.assertEqual(LeafViewedBy.objects.count(), 0)
        self.assertEqual(LeafInteraction.objects.count(), 0)
        self.assertEqual(UserTopicRelations.objects.count(), 0)
        self.assertEqual(UserLeafPreferences.objects.count(), 0)