import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from eden_utils.leaf_management import EdenLeafManagement

ELM_object = EdenLeafManagement()


def return_response(map):
    return HttpResponse(content=json.dumps(map))


def create_leaf_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['text_content', 'leaf_type']
        condition = True
        for field in valid_fields:
            if field not in data.keys():
                condition = False
        if condition:
            response = ELM_object.create_leaf(request, request.body)
            return return_response(response)
        else:
            response = {}
            response['messaage'] = "Valid fields not found in request body"
            response['status'] = 200
            return return_response(response)


def get_user_public_leaves_view(request):
    if request.method == "GET":
        data = json.loads(request.body)
        response = {}
        response_status = ELM_object.get_user_public_leaves(request)
        if response_status == -101:
            response['message'] = 'Auth Error.'
            return response
        else:
            return JsonResponse(response.values())


def get_user_private_leaves_view(request):
    if request.method == "GET":
        data = json.loads(request.body)
        response = {}
        response_status = ELM_object.get_user_private_leaves(request)
        if response_status == -101:
            response['message'] = 'Auth Error.'
            return response
        else:
            return JsonResponse(response.values())


def delete_leaf_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id']
        condition = True
        for field in valid_fields:
            if field not in data.keys():
                condition = False
        if condition:
            response = ELM_object.delete_leaf(request, data['leaf_id'])
            return return_response(response)
        else:
            response = {}
            response['messaage'] = "Valid fields not found in request body"
            response['status'] = 200
            return return_response(response)


def like_leaf_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id']
        condition = True
        for field in valid_fields:
            if field not in data.keys():
                condition = False
        if condition:
            response = ELM_object.like_leaf(request, data['leaf_id'])
            return return_response(response)
        else:
            response = {}
            response['messaage'] = "Valid fields not found in request body"
            response['status'] = 200
            return return_response(response)


def dislike_leaf_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id']
        condition = True
        for field in valid_fields:
            if field not in data.keys():
                condition = False
        if condition:
            response = ELM_object.dislike_leaf(request, data['leaf_id'])
            return return_response(response)
        else:
            response = {}
            response['messaage'] = "Valid fields not found in request body"
            response['status'] = 200
            return return_response(response)


def add_comment_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id', 'comment_string']
        condition = True
        for field in valid_fields:
            if field not in data.keys():
                condition = False
        if condition:
            response = ELM_object.add_comment(request, data['leaf_id'], data['comment_string'])
            return return_response(response)
        else:
            response = {}
            response['messaage'] = "Valid fields not found in request body"
            response['status'] = 200
            return return_response(response)


def remove_comment_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id']
        condition = True
        for field in valid_fields:
            if field not in data.keys():
                condition = False
        if condition:
            response = ELM_object.remove_comment(request, data['leaf_id'])
            return return_response(response)
        else:
            response = {}
            response['messaage'] = "Valid fields not found in request body"
            response['status'] = 200
            return return_response(response)


def get_all_likes(request):
    if request.method == "GET":
        data = json.loads(request.body)
        response = {}
        valid_fields = ['leaf_id']
        condition = True
        for field in valid_fields:
            if field not in data.keys():
                condition = False
        if condition:
            response = ELM_object.get_total_likes(request, data['leaf_id'])
            return JsonResponse(response.values())
        else:
            response = {}
            response['messaage'] = "Valid fields not found in request body"
            response['status'] = 200
            return return_response(response)


def get_all_comments(request):
    if request.method == "GET":
        data = json.loads(request.body)
        response = {}
        valid_fields = ['leaf_id']
        condition = True
        for field in valid_fields:
            if field not in data.keys():
                condition = False
        if condition:
            response = ELM_object.get_total_comment(request, data['leaf_id'])
            return JsonResponse(response.values())
        else:
            response = {}
            response['messaage'] = "Valid fields not found in request body"
            response['status'] = 200
            return return_response(response)
