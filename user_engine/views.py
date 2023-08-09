import json


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
            data = json.loads(request.body)
            pre_response = user_control_object.create_user(data)
            print(pre_response)
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
        except:
            return make_response({"status": 200, "message": "Cannot unload data."})
    return make_response({"status": 200, "message": "HTTP method is not supported."})



@csrf_exempt
def follow_user_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            pre_response = user_control_object.user_follow(data)
            return make_response({"status": 200, "message": str(pre_response)})
        except:
            return make_response({"status": 200, "message": "Cannot unload data."})
    return make_response({"status": 200, "message": "HTTP method is not supported."})


@csrf_exempt
def unfollow_user_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            pre_response = user_control_object.user_unfollow(data)
            return make_response({"status": 200, "mess age": str(pre_response)})
        except:
            return make_response({"status": 200, "message": "Cannot unload data."})

    return make_response({"status": 200, "message": "HTTP method is not supported."})


@csrf_exempt
def get_followers(request):
    if request.method == "GET":
        try:
            data = json.loads(request.body)
            pre_response = user_control_object.get_user_followers(data)
            response = JsonResponse(pre_response, safe=False)
            return response
        except Exception as e:
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})


@csrf_exempt
def get_following(request):
    if request.method == "GET":
        try:
            data = json.loads(request.body)
            pre_response = user_control_object.get_user_following(data)
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
                session_management_object.create_session(request, user)
                return make_response({"status": 200, "message": "Login successful."})

            return make_response({"status": 200, "message": "Login failed."})

        except Exception as e:
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})


@csrf_exempt
def logout(request):
    if request.method == "POST":
        try:
            session_management_object.delete_session(request)
        except KeyError:
            pass
        return HttpResponse("You're logged out.")
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})


@csrf_exempt
def current_user(request):
    if request.method == "GET":
        user = session_management_object.get_session_user(request)
        return make_response({
            'status': 200,
            'user_name': user.user_name if user is not None else None
        })
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
        except:
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})

@csrf_exempt
def get_user_details(request):
    if request.method == "GET":
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
                    "user_phone_id":user_data.user_phone_id
                })
        except Exception as e:
            print(e)
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
                            "user_phone_id"]
            if check_field_validity(valid_fields,data):
                user_id = user_control_object.add_user_details(data)
                return make_response(user_id)
        except Exception as e:
            print(e)
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})

@csrf_exempt
def block_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['blocked']
            if check_field_validity(valid_fields,data):
                user_id = user_control_object.add_user_blocked(data)
                return make_response(user_id)
        except Exception as e:
            print(e)
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})


@csrf_exempt
def unblock_user(request):
    if request.method == "GET":
        try:
            data = json.loads(request.body)
            valid_fields = ['blocked']
            if check_field_validity(valid_fields,data):
                user_id = user_control_object.unblock_user(data)
                return make_response(user_id)
        except:
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
                return make_response(user_id)
        except Exception as e:
            print(e)
            return make_response({"status": 200, "message": "Cannot unload data."})
    else:
        return make_response({"status": 200, "message": "HTTP method is not supported."})


def get_logged_in_user(request):
    return session_management_object.get_session_user(request)

