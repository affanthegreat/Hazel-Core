import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .leaf_management import EdenLeafManagement
from leaf_engine.communicator import EdenLeafCommunicator

ELM_object = EdenLeafManagement()
communicator_object = EdenLeafCommunicator()

def make_http_response(map):
    return HttpResponse(content= json.dumps(map))

def make_json_response(map):
    return  JsonResponse(map)

def check_field_validity(data,valid_fields):
    condition = True
    for field in valid_fields:
        if field not in data.keys():
            condition = False
    return condition

def throw_invalid_fields_error():
    response = {}
    response['messaage'] = "Valid fields not found in request body"
    response['status'] = 200
    return make_http_response(response)

def throw_http_method_not_supported_error():
     return HttpResponse(
            content=json.dumps({"status": 200, "message": "HTTP method is not supported."})
        )

@csrf_exempt
def stream_uncategorized_leaves_view(request):
    if request.method == "GET":
        data = json.loads(request.body)
        valid_fields = ['page_number']
        if check_field_validity(data,valid_fields):
            response = communicator_object.stream_uncategorized_leaves(data)
            return make_json_response(response)
        else:
            return throw_invalid_fields_error()
    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def stream_leaves_topic_wise_view(request):
    if request.method == "GET":
        data = json.loads(request.body)
        valid_fields = ['page_number','topic_id']
        if check_field_validity(data,valid_fields):
            response = communicator_object.stream_leaves_topic_wise(data)
            return make_json_response(response)
        else:
            return throw_invalid_fields_error()
    else:
       return throw_http_method_not_supported_error()


@csrf_exempt
def stream_negative_leaves_view(request):
    if request.method == "GET":
        data = json.loads(request.body)
        valid_fields = ['page_number']
        if check_field_validity(data, valid_fields):
            response = communicator_object.stream_negative_leaves(data)
            return make_json_response(response)
        else:
           return throw_invalid_fields_error()

    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def stream_unmarked_comments_view(request):
    if request.method == "GET":
        data = json.loads(request.body)
        valid_fields = ['page_number']
        if check_field_validity(data, valid_fields):
            response = communicator_object.stream_unmarked_comments(data)
            return make_json_response(response)
        else:
            return throw_invalid_fields_error()

    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def stream_marked_comments_view(request):
    if request.method == "GET":
        data = json.loads(request.body)
        valid_fields = ['page_number']
        if check_field_validity(data, valid_fields):
            response = communicator_object.stream_marked_comments(data)
            return make_json_response(response)
        else:
            return throw_invalid_fields_error()

    else:
        return throw_http_method_not_supported_error()

@csrf_exempt
def get_leaf_metrics_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id']
        if check_field_validity(data, valid_fields):
            response = communicator_object.send_leaf_metrics(data)
            return make_json_response(response)
        else:
            return throw_invalid_fields_error()

    else:
        return throw_http_method_not_supported_error()

@csrf_exempt
def update_batch_leaf_metrics_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['batch_number','leaves_collection']
        if check_field_validity(data, valid_fields):
            response = communicator_object.send_leaf_metrics(data['leaves_collection'])
            return make_http_response(response)
        else:
            return throw_invalid_fields_error()

    else:
        return throw_http_method_not_supported_error()
