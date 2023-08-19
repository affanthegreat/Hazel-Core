import json
import logging

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate
from django.core import serializers

from user_engine.backends import EdenSessionManagement

from .user_management import EdenUserManagement

user_control_object = EdenUserManagement()
session_management_object = EdenSessionManagement()


def make_response(data):
    return HttpResponse(content=json.dumps(data))

def check_field_validity(valid_fields, data):
    condition = True
    for field in valid_fields:
            if field not in data.keys():
                condition = False
    return condition


@csrf_exempt
def create_user_api(request):
    if request.method == "POST":
        try:
            request
            data = json.loads(request.body)
            pre_response = user_control_object.create_user(data)
            return make_response({"status": 200, "message": pre_response["issue"]})
        except Exception as E:
            return make_response({"status": 200,
                                     "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})

@csrf_exempt
def validate_user_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            pre_response = user_control_object.validate_user(data)
            return make_response({"status": 200, "message": str(pre_response)})
        except Exception as E:
            return make_response({"status": 200, "message": "Cannot unload data."})
    return make_response({"status": 200, "message": "HTTP method is not supported."})



@csrf_exempt
def follow_user_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            pre_response = user_control_object.user_follow(data)
            return make_response({"status": 200, "message": str(pre_response['message'])})
        except Exception as e:
            return make_response({"status": 200, "message": "Cannot unload data."})
    return make_response({"status": 200, "message": "HTTP method is not supported."})


@csrf_exempt
def unfollow_user_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            pre_response = user_control_object.user_unfollow(data)
            return make_response({"status": 200, "message": str(pre_response['message'])})
        except:
            return make_response({"status": 200, "message": "Cannot unload data."})

    return make_response({"status": 200, "message": "HTTP method is not supported."})


@csrf_exempt
def get_followers(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            pre_response = user_control_object.get_user_followers(data)
            print(pre_response)
            response = make_response(pre_response)
            return response
        except Exception as e:
            raise e
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})


@csrf_exempt
def get_following(request):
    if request.method == "GET":
        try:
            data = json.loads(request.body)
            pre_response = user_control_object.get_user_following(data)
            print(pre_response)
            response = JsonResponse(pre_response, safe=False)
            return response
        except Exception as e:
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})


@csrf_exempt
def login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data["user_name"]
            password = data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                token, auth_token = session_management_object.create_session(request, user)
                return make_response({"status": 200, "message": "Login successful.", 'token':token, 'auth_token': auth_token})

            return make_response({"status": 200, "message": "Login failed."})

        except Exception as e:
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})


@csrf_exempt
def logout(request):
    if request.method == "POST":
        try:
            session_management_object.load_session(request, json.loads(request.data))
            session_management_object.delete_session(request)
            return make_response({'status':200, 'message': "Logout successful.", })
        except:
            return make_response({'status':200, 'message': "Logout failed."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})


@csrf_exempt
def current_user(request):
    if request.method == "POST":
        user = session_management_object.get_session_user(request)
        return make_response({
            'status': 200,
            'user_name': user.user_name if user is not None else None
        })
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})
    

@csrf_exempt
def check_follow(request):
    if request.method == "POST":
        data = json.loads(request.body)
        response = user_control_object.check_follow(data['user_id'], data['search_profile_id'])
        return make_response(response)
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})

@csrf_exempt
def password_reset(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            if get_logged_in_user(request):
                pre_response = user_control_object.password_reset(data)
                return HttpResponse(content=json.dumps({
                    'status': 200,
                    'message': pre_response['message']
                }))
            else:
                return make_response({"status": 200, "message": "User not logged in."})
        except:
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})

@csrf_exempt
def get_user_details(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['user_id']
            if check_field_validity(valid_fields,data):
                user_data = user_control_object.get_user_detail_object(data['user_id'])
                return make_response({
                    'user_id':user_data.user_id.user_id,
                    "user_full_name": user_data.user_full_name, 
                    "user_phone_number": user_data.user_phone_number,
                    "user_address":user_data.user_address, 
                    "user_phone_id":user_data.user_phone_id,
                     "user_ip_location": user_data.user_ip_location,
                    "user_city": user_data.user_city,
                    "user_gender": user_data.user_gender,
                    "user_dob": str(user_data.user_dob)
                })
        except Exception as e:

            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})

@csrf_exempt
def modify_user_details(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['user_id',
                            "user_full_name", 
                            "user_phone_number",
                            "user_address", 
                            "user_phone_id",
                            "user_ip_location",
                            "user_city",
                            "user_gender",
                            "user_dob"
                            ]
            if check_field_validity(valid_fields,data):
                user_control_object.add_user_details(data)
                return make_response({"message": "Sucess"})
            else:
                print(valid_fields)
                print(data.keys())
                return make_response({"status": 200, "message": "Cannot unload data."})
        except Exception as e:
            raise e
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})


@csrf_exempt
def add_user_private_relation(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['main_user', 'secondary_user']
            if check_field_validity(valid_fields,data):
                response = user_control_object.add_user_private_leaf_model(data)
                return make_response({"message":str(response)})
        except Exception as e:
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})

@csrf_exempt
def remove_user_private_relation(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['main_user', 'secondary_user']
            if check_field_validity(valid_fields,data):
                response = user_control_object.remove_user_private_leaf_model(data)
                return make_response({"message":str(response)})
        except Exception as e:
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})



@csrf_exempt
def block_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['blocked', 'auth_token', 'token']
            if check_field_validity(valid_fields,data):
                data['user_id'] = get_logged_in_user(request).user_id
                response = user_control_object.add_user_blocked(data)
                return make_response({"message":str(response)})
        except Exception as e:
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})


@csrf_exempt
def unblock_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['blocked', 'auth_token', 'token']
            if check_field_validity(valid_fields,data):
                data['user_id'] = get_logged_in_user(request).user_id
                response = user_control_object.unblock_user(data)
                return make_response({"message":str(response)})
        except Exception as e:
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})


@csrf_exempt
def make_follow_request_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['requested_to','auth_token', 'token' ]
            if check_field_validity(valid_fields,data):
                data['requester'] = get_logged_in_user(request).user_id
                response = user_control_object.create_follow_request(data)
                return make_response({"message":str(response)})
        except Exception as e:
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})


@csrf_exempt
def remove_follow_request_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['requested_to','auth_token', 'token' ]
            if check_field_validity(valid_fields,data):
                data['requester'] = get_logged_in_user(request).user_id
                response = user_control_object.remove_follow_request(data)
                return make_response({"message":str(response)})
        except Exception as e:
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})

@csrf_exempt
def fetch_all_follow_request_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['requested_to']
            if check_field_validity(valid_fields,data):
                response = user_control_object.fetch_all_follow_requests(data)
                return make_response({"message":str(response)})
        except Exception as e:
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})

@csrf_exempt
def accept_follow_request(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['request_id']
            if check_field_validity(valid_fields,data):
                response = user_control_object.accept_follow_request(data['request_id'])
                return make_response({"message":str(response)})
        except Exception as e:
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})


@csrf_exempt
def delete_follow_request(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['request_id']
            if check_field_validity(valid_fields,data):
                response = user_control_object.deny_follow_request(data['request_id'])
                return make_response({"message":str(response)})
        except Exception as e:
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})


@csrf_exempt
def get_user_id(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['user_name']
            if check_field_validity(valid_fields,data):
                user_id = user_control_object.get_user_id(data)
                return make_response({'user_id':user_id})
        except Exception as e:
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})


@csrf_exempt
def check_user_exists(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            status = user_control_object.check_user_exists(data)
            if status:
                return make_response({'status':200, 'message': "User Exists."})
            else:
                return make_response({'status':200, 'message': "User Does not Exists."})
        except Exception as e:
            return make_response({'status':200, 'message': "Error Occured"})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})

@csrf_exempt
def get_user_info(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            status = user_control_object.get_user_info(data)
            if status:
                return make_response(status)
            else:
                return make_response({'status':200, 'message': "User Does not Exists."})
        except Exception as e:
            return make_response({'status':200, 'message': "Error Occured"})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})

@csrf_exempt
def search_users(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            status = user_control_object.get_searched_users(data['search_query'], data['page_number'])
            if status:
                return make_response(status)
            else:
                return make_response({'status':200, 'message': "User Does not Exists."})
        except Exception as e:
            raise e
            return make_response({'status':200, 'message': "Error Occured"})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})


def get_logged_in_user(request):
    return session_management_object.get_session_user(request)

