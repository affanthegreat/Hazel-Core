import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from admax_engine.admax_manager import Eden_ADMAX_Engine

admax_object = Eden_ADMAX_Engine()

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

def throw_invalid_fields_error(E):
    response = {}
    response['messaage'] = f"Valid fields not found in request body {E}"
    response['status'] = 200
    return make_http_response(response) 

def throw_http_method_not_supported_error():
     return HttpResponse(
            content=json.dumps({"status": 200, "message": "HTTP method is not supported."})
        )

@csrf_exempt
def create_advertisement_campaign(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['user_object', 'campaign_name']
            if check_field_validity(valid_fields, data):
                pre_response = admax_object.create_advertisement_campaign(request, data)
                return make_http_response(pre_response)
            else:
                return throw_invalid_fields_error("")
        except Exception as E:
            return throw_invalid_fields_error(E)
    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def create_advertisement_instance(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['campaign_id', 'leaf_id', 'target_topic_id', 'advertisement_tier']
            if check_field_validity(valid_fields, data):
                pre_response = admax_object.create_advertisement_instance(request, data)
                return make_http_response(pre_response)
            else:
                return throw_invalid_fields_error("")
        except Exception as E:
            return throw_invalid_fields_error(E)
    else:
        return throw_http_method_not_supported_error()
    

@csrf_exempt
def delete_ad(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['leaf_id']
            if check_field_validity(valid_fields, data):
                pre_response = admax_object.delete_ad(request, data)
                return make_http_response(pre_response)
            else:
                return throw_invalid_fields_error("")
        except Exception as E:
            return throw_invalid_fields_error(E)
    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def delete_campaign(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['campaign_id']
            if check_field_validity(valid_fields, data):
                pre_response = admax_object.delete_campaign(request, data)
                return make_http_response(pre_response)
            else:
                return throw_invalid_fields_error("")
        except Exception as E:
            return throw_invalid_fields_error(E)
    else:
        return throw_http_method_not_supported_error()

@csrf_exempt
def get_ad_analytics(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['leaf_id']
            if check_field_validity(valid_fields, data):
                pre_response = admax_object.get_ad_analytics(data['leaf_id'])
                return make_http_response(pre_response)
            else:
                return throw_invalid_fields_error("")
        except Exception as E:
            return throw_invalid_fields_error(E)
    else:
        return throw_http_method_not_supported_error()
    

@csrf_exempt
def get_campaign_summary(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['campaign_id']
            if check_field_validity(valid_fields, data):
                pre_response = admax_object.get_campaign_summary(data['campaign_id'])
                return make_http_response(pre_response)
            else:
                return throw_invalid_fields_error("")
        except Exception as E:
            return throw_invalid_fields_error(E)
    else:
        return throw_http_method_not_supported_error()
    


@csrf_exempt
def create_promoted_leaf(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['leaf_id', 'boost_multiplier', 'duration']
            if check_field_validity(valid_fields, data):
                pre_response = admax_object.create_promoted_leaf(data['campaign_id'])
                return make_http_response(pre_response)
            else:
                return throw_invalid_fields_error("")
        except Exception as E:
            return throw_invalid_fields_error(E)
    else:
        return throw_http_method_not_supported_error()



@csrf_exempt
def remove_promoted_leaf(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['leaf_id',]
            if check_field_validity(valid_fields, data):
                pre_response = admax_object.remove_promoted_status(data['leaf_id'])
                return make_http_response(pre_response)
            else:
                return throw_invalid_fields_error("")
        except Exception as E:
            return throw_invalid_fields_error(E)
    else:
        return throw_http_method_not_supported_error()


def make_leaf_into_promoted_leaf(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['leaf_id', 'boost_multiplier', 'duration']
            if check_field_validity(valid_fields, data):
                pre_response = admax_object.make_leaf_into_promoted_leaf(data['leaf_id'], data['boost_multiplier'], data['duration'])
                return make_http_response(pre_response)
            else:
                return throw_invalid_fields_error("")
        except Exception as E:
            return throw_invalid_fields_error(E)
    else:
        return throw_http_method_not_supported_error()
    