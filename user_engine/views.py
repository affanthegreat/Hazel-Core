import json

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from eden_utils.user_management import EdenUserManagement

user_control_object = EdenUserManagement()


@csrf_exempt
def create_user_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        pre_response = user_control_object.create_user(data)
        print(pre_response)
        return HttpResponse(content={
            'status': 200,
            'message': pre_response["issue"]
        })


@csrf_exempt
def validate_user_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        pre_response = user_control_object.validate_user(data)
        return HttpResponse(content={
            'status': 200,
            'message': str(pre_response)
        })


@csrf_exempt
def follow_user_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        pre_response = user_control_object.user_follow(data)
        print(pre_response)
        return HttpResponse(content={
            'status': 200,
            'message': str(pre_response)
        })


@csrf_exempt
def get_followers(request):
    if request.method == "POST":
        data = json.loads(request.body)
        pre_response = user_control_object.get_user_followers(data)
        print(pre_response)
        return HttpResponse(content={
            'status': 200,
            'message': str(pre_response)
        })


@csrf_exempt
def get_following(request):
    if request.method == "POST":
        data = json.loads(request.body)
        pre_response = user_control_object.get_user_following(data)
        print(pre_response)
        return HttpResponse(content={
            'status': 200,
            'message': str(pre_response)
        })
