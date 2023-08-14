import json
from django.test import TestCase, Client
from django.urls import reverse

from user_engine.user_management import EdenUserManagement
from user_engine.models import *

user_control_object = EdenUserManagement()

def to_dict(json_obj):
    return json.loads(json_obj)

class EdenUserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_user(self):
        test_data = {
             'user_name': "test1",
             'user_email': 'test1@example.com',
             'user_password': 'something',
            }
        url = reverse('create_user')
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], 'Success')
    
    def test_invalid_password(self):
        test_data = {
             'user_name': "test1",
             'user_email': 'test1@example.com',
             'user_password': 'some',
            }
        url = reverse('create_user')
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], 'Password too short')
    
    def test_invalid_email(self):
        test_data = {
             'user_name': "test1",
             'user_email': 'test1@example',
             'user_password': 'something',
            }
        url = reverse('create_user')
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], 'Not a valid email')

    
    def test_create_user(self):
        test_data = {
             'user_name': "test1",
             'user_email': 'test1@example.com',
             'user_password': 'something',
            }
        url = reverse('create_user')
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], 'Success')

    def test_check_user_exists_non_existent_user(self):
        test_data ={'user_id':user_control_object.get_user_id({'user_name':'test1'})}
        self.assertEqual(user_control_object.check_user_exists(test_data), False)
    
    def test_check_user_exists(self):
        test_data = {
             'user_name': "test1",
             'user_email': 'test1@example.com',
             'user_password': 'something',
            }
        url = reverse('create_user')
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], 'Success') 
        self.assertEqual(user_control_object.check_user_exists(test_data), True)      
    
class ExistingUserTestCase(TestCase):
    def setUp(self):
        self.test_data = {
             'user_name': "test1",
             'user_email': 'test1@example.com',
             'user_password': 'something',
            }
        user_control_object.create_user(self.test_data)
        self.test_user_1_id = user_control_object.get_user_id(self.test_data)


    def test_duplicate_user(self):
        url = reverse('create_user')
        response = self.client.post(url, self.test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], 'User already exists')
    
    def test_check_user_exists(self):
        test_data ={'user_id':user_control_object.get_user_id({'user_name':self.test_data['user_name']})}
        self.assertEqual(user_control_object.check_user_exists(test_data), True)
    
    def test_validate_user_data(self):
        url = reverse('validate_data')
        test_data ={'user_id':user_control_object.get_user_id({'user_name':self.test_data['user_name']}), 'user_password': self.test_data['user_password']}
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], 'True')
    
    def test_get_user_id(self):
        url = reverse('get_user_id')
        response = self.client.post(url, self.test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['user_id'], user_control_object.get_user_id({'user_name':self.test_data['user_name']}))

    def test_user_add_details(self):
        get_url= reverse('get_user_details')
        modify_url = reverse('modify_user_details')
        test_data = {
            'user_id': user_control_object.get_user_id({'user_name':'test1'}),
            'user_full_name': 'Big goofus',
            'user_phone_number': '696969696969',
            'user_address': 'planet earth',
            'user_phone_id': 'user_phone_id',
            'user_ip_location':"india",
            'user_city':'hyderabad',
            'user_gender':'batman',
            'user_dob':str(datetime.datetime.now().date())
        }
        modify_response = self.client.post(modify_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(modify_response.content)['message'],"Sucess")
        get_response = self.client.post(get_url, {'user_id': self.test_user_1_id},  content_type='application/json')
        get_body = to_dict(get_response.content)
        get_body['user_id'] = test_data['user_id']
        self.assertEqual(get_body,test_data)
        
        
class UserFunctionTestCase(TestCase):
    def setUp(self):
        self.client = Client()
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
        self.url = reverse('follow')
        user_control_object.create_user(self.test_user_1)
        user_control_object.create_user(self.test_user_2)
        self.test_user_1_id = user_control_object.get_user_id(self.test_user_1)
        self.test_user_2_id = user_control_object.get_user_id(self.test_user_2)

    def test_user_follow(self):
        test_data = {'follower':self.test_user_1_id, 'follows':self.test_user_2_id}
        response = self.client.post(self.url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], 'test1 added as follower to test2')
        self.assertEqual(UserFollowing.objects.count(), 1)
    
    def test_user_following(self):
        test_data = {'follows':self.test_user_1_id, 'follower':self.test_user_2_id}
        response = self.client.post(self.url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], 'test2 added as follower to test1')
        self.assertEqual(UserFollowing.objects.count(), 1)
    
    def test_follow_non_existing_user(self):
        test_data = {'follower':self.test_user_1_id, 'follows':"test3"}
        response = self.client.post(self.url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], 'One of the user does not exists.')

    def test_already_follows(self):
        test_data = {'follower':self.test_user_1_id, 'follows':self.test_user_2_id}
        user_control_object.user_follow(test_data)
        response = self.client.post(self.url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], 'test1 already follows test2')

    def test_user_unfollow(self):
        url = reverse('unfollow')
        test_data = {'follower':self.test_user_1_id, 'follows':self.test_user_2_id}
        user_control_object.user_follow(test_data)
        self.assertEqual(UserFollowing.objects.count(), 1)
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], 'test1 successfully unfollowed test2')
        self.assertEqual(UserFollowing.objects.count(), 0)
    
    def test_user_unfollow_if_user_does_not_follow(self):
        url = reverse('unfollow')
        test_data = {'follower':self.test_user_1_id, 'follows':self.test_user_2_id}
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "test1 doesn't follow test2")
    
    def test_unfollow_non_existing_user(self):
        url = reverse('unfollow')
        test_data = {'follower':self.test_user_1_id, 'follows':"test3"}
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], 'One of the user does not exists.')

    def test_add_user_private_relation(self):
        url = reverse('add_user_private_relation')
        test_data = {'main_user':self.test_user_1_id, 'secondary_user':self.test_user_2_id}
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], '100')
        self.assertEqual(UserPrivateRelation.objects.count(), 1)
    
    def test_add_user_private_relation_invalid_user(self):
        url = reverse('add_user_private_relation')
        test_data = {'main_user':"NON EXISTANT", 'secondary_user':self.test_user_2_id}
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], '102')
        self.assertEqual(UserPrivateRelation.objects.count(), 0)
    
    def test_remove_user_private_relation_non_existing_relation(self):
        url = reverse('add_user_private_relation')
        test_data = {'main_user':self.test_user_1_id, 'secondary_user':self.test_user_2_id}
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], '100')
        self.assertEqual(UserPrivateRelation.objects.count(), 1)
    
        url = reverse('remove_user_private_relation')
        test_data = {'main_user':self.test_user_1_id, 'secondary_user':self.test_user_2_id}
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], '100')
        self.assertEqual(UserPrivateRelation.objects.count(), 0)

    def test_remove_user_private_relation(self):
        url = reverse('remove_user_private_relation')
        test_data = {'main_user':self.test_user_1_id, 'secondary_user':self.test_user_2_id}
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], '102')
        self.assertEqual(UserPrivateRelation.objects.count(), 0)

    def test_user_block(self):
        url = reverse('login')
        response = self.client.post(url, self.test_user_1,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "Login successful.")
        self.assertEqual(UserAccessToken.objects.count(), 1)
        block_url = reverse('block_user')
        test_data = {'blocked': self.test_user_2_id}
        response = self.client.post(block_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "100")
        self.assertEqual(UserBlockedAccounts.objects.count(), 1)
    
    def test_user_unblock(self):
        url = reverse('login')
        response = self.client.post(url, self.test_user_1,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "Login successful.")
        self.assertEqual(UserAccessToken.objects.count(), 1)
        block_url = reverse('block_user')
        test_data = {'blocked': self.test_user_2_id}
        response = self.client.post(block_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "100")
        self.assertEqual(UserBlockedAccounts.objects.count(), 1)
        block_url = reverse('unblock_user')
        test_data = {'blocked': self.test_user_2_id}
        response = self.client.post(block_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "100")
        self.assertEqual(UserBlockedAccounts.objects.count(), 0)

    
class EdenUserLoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_user = {
             'user_name': "test1",
             'user_email': 'test1@example.com',
             'user_password': 'something',
             'password': 'something'
            }

        user_control_object.create_user(self.test_user)
    
    def test_successful_login(self):
        url = reverse('login')
        response = self.client.post(url, self.test_user,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "Login successful.")
        self.assertEqual(UserAccessToken.objects.count(), 1)
    
    def test_invalid_password(self):
        url = reverse('login')
        test_data = self.test_user.copy()
        test_data['password'] = 'somethig'
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "Login failed.")
    
    def test_invalid_user(self):
        url = reverse('login')
        test_data = self.test_user.copy()
        test_data['user_name'] = 'test3'
        response = self.client.post(url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "Login failed.")

    def test_logout(self):
        login_url = reverse('login')
        logout_url = reverse('logout')
        login_response = self.client.post(login_url, self.test_user,  content_type='application/json')
        self.assertEqual(UserAccessToken.objects.count(), 1)
        logout_response = self.client.post(logout_url, self.test_user,  content_type='application/json')
        self.assertEqual(to_dict(login_response.content)['message'], "Login successful.")
        self.assertEqual(to_dict(logout_response.content)['message'], "Logout successful.")
        self.assertEqual(UserAccessToken.objects.count(), 0)
    
    def test_login_without_logout(self):
        logout_url = reverse('logout')
        logout_response = self.client.post(logout_url, self.test_user,  content_type='application/json')
        self.assertEqual(to_dict(logout_response.content)['message'], "Logout failed.")
    
    def test_current_user(self):
        login_url = reverse('login')
        current_url = reverse('current_user')
        login_response = self.client.post(login_url, self.test_user,  content_type='application/json')
        current_user_response = self.client.get(current_url, self.test_user,  content_type='application/json')
        self.assertEqual(to_dict(login_response.content)['message'], "Login successful.")
        self.assertEqual(to_dict(current_user_response.content)['user_name'], "test1")
    
    def test_current_user_without_login(self):
        current_url = reverse('current_user')
        current_user_response = self.client.get(current_url, self.test_user,  content_type='application/json')
        self.assertEqual(to_dict(current_user_response.content)['user_name'], None)
    
    def test_password_reset_without_login(self):
        password_reset_url = reverse('password_reset')
        login_url = reverse('login')
        test_data = {
            'user_id': user_control_object.get_user_id(self.test_user),
            'user_password': self.test_user['password'],
            'user_name': self.test_user['user_name'],
            'user_password1': 'something2',
            'user_password2': 'something2'
        }
        response = self.client.post(password_reset_url, self.test_user,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'],  'User not logged in.')
    
    def test_password_reset(self):
        password_reset_url = reverse('password_reset')
        login_url = reverse('login')
        logout_url = reverse('logout')
        test_data = {
            'user_id': user_control_object.get_user_id(self.test_user),
            'user_password': self.test_user['password'],
            'user_name': self.test_user['user_name'],
            'user_password1': 'something2',
            'user_password2': 'something2'
        }
        login_response = self.client.post(login_url, self.test_user,  content_type='application/json')
        self.assertEqual(to_dict(login_response.content)['message'], "Login successful.")
        response = self.client.post(password_reset_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "Password changed sucessfully")
        logout_response = self.client.post(logout_url, self.test_user,  content_type='application/json')
        self.assertEqual(to_dict(logout_response.content)['message'], "Logout successful.")
        login_response = self.client.post(login_url, self.test_user,  content_type='application/json')
        self.assertEqual(to_dict(login_response.content)['message'], "Login failed.")
    
    def test_password_reset_wrong_user_pass(self):
        password_reset_url = reverse('password_reset')
        login_url = reverse('login')
        test_data = {
            'user_id': user_control_object.get_user_id(self.test_user),
            'user_password': "random",
            'user_name': self.test_user['user_name'],
            'user_password1': 'something2',
            'user_password2': 'something2'
        }
        login_response = self.client.post(login_url, self.test_user,  content_type='application/json')
        self.assertEqual(to_dict(login_response.content)['message'], "Login successful.")
        response = self.client.post(password_reset_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "Invalid current password")

    def test_password_reset_new_password_mismatch(self):
        password_reset_url = reverse('password_reset')
        login_url = reverse('login')
        test_data = {
            'user_id': user_control_object.get_user_id(self.test_user),
            'user_password': self.test_user['password'],
            'user_name': self.test_user['user_name'],
            'user_password1': 'something2',
            'user_password2': 'something1'
        }
        login_response = self.client.post(login_url, self.test_user,  content_type='application/json')
        self.assertEqual(to_dict(login_response.content)['message'], "Login successful.")
        response = self.client.post(password_reset_url, test_data,  content_type='application/json')
        self.assertEqual(to_dict(response.content)['message'], "New passwords does not match")
    
