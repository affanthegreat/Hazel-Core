import json

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth import authenticate

from eden_utils.user_management import EdenUserManagement
from user_engine.backends import EdenSessionManagement

user_control_object = EdenUserManagement()


@csrf_exempt
def create_user_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        pre_response = user_control_object.create_user(data)
        print(pre_response)
        return HttpResponse(content=json.dumps({
            'status': 200,
            'message': pre_response["issue"]
        }))




@csrf_exempt
def validate_user_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        pre_response = user_control_object.validate_user(data)
        return HttpResponse(content=json.dumps({
            'status': 200,
            'message': str(pre_response)
        }))


@csrf_exempt
def follow_user_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        pre_response = user_control_object.user_follow(data)
        return HttpResponse(content=json.dumps({
            'status': 200,
            'message': str(pre_response)
        }))


@csrf_exempt
def get_followers(request):
    if request.method == "POST":
        data = json.loads(request.body)
        pre_response = user_control_object.get_user_followers(data)
        return HttpResponse(content=json.dumps({
            'status': 200,
            'message': str(pre_response)
        }))


@csrf_exempt
def get_following(request):
    if request.method == "POST":
        data = json.loads(request.body)
        pre_response = user_control_object.get_user_following(data)
        return HttpResponse(content=json.dumps({
            'status': 200,
            'message': str(pre_response)
        }))


@csrf_exempt
def login(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data['user_name']
        password = data['password']
        user = authenticate(request, username=username, password=password)
 
        if user != None:
            session_management_object = EdenSessionManagement()
            session_management_object.create_session(request,user)
            return HttpResponse(content=json.dumps({
            'status': 200,
            'message': "Login successful."
        }))

        return HttpResponse(content=json.dumps({
            'status': 200,
            'message': "Login failed."
        }))

@csrf_exempt
def logout(request):
    try:
        session_management_object = EdenSessionManagement()
        session_management_object.delete_session(request)
    except KeyError:
        pass
    return HttpResponse("You're logged out.")


@csrf_exempt
def current_user(request):
     return HttpResponse(content=json.dumps({
            'status': 200,
            'user_id': request.session.get('user_name',None)
        }))