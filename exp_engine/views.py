import json

from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate

from exp_engine.exp_manager import *
from exp_engine.exp_recommender import HazelRecommendationEngine


exp_engine_instance = EdenExperienceEngine()
recommendation_engine= HazelRecommendationEngine()


def check_field_validity(valid_fields, data):
    condition = True
    for field in valid_fields:
            if field not in data.keys():
                condition = False
    return condition

def make_http_response(data_map):
    return HttpResponse(
                content=json.dumps(data_map)
            )

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
def initiate_exp_engine(request):
    if request.method == "POST":
        try:
            pre_response = exp_engine_instance.batch_initiate(request)

            return make_http_response(pre_response)
        except Exception as E:
            return throw_invalid_fields_error()
    else:
        return throw_http_method_not_supported_error()



@csrf_exempt
def initiate_exp_engine_per_leaf(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['leaf_id']
            print(data, check_field_validity(valid_fields,data))
            if check_field_validity(valid_fields, data):
                response = exp_engine_instance.initiate_per_leaf_view(data['leaf_id'])
                return make_http_response(response)
            else:
                return throw_invalid_fields_error()
        except Exception as E:
            raise E
    else:
        return throw_http_method_not_supported_error()
    

@csrf_exempt
def get_recommended_posts(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['page_number']
            if check_field_validity(valid_fields, data):
                user_object = get_logged_in_user(request)
                response = recommendation_engine.initiate(user_object.user_id, data['page_number'])
                return make_http_response(response)
            else:
                return throw_invalid_fields_error()
        except Exception as E:
            raise E
    else:
        return throw_http_method_not_supported_error()
    
def get_logged_in_user(request):
    return exp_engine_instance.get_logged_in_user(request)