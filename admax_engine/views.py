import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from user_engine.user_management import EdenUserManagement
from admax_engine.admax_manager import Eden_ADMAX_Engine

admax_object = Eden_ADMAX_Engine()
user_management_object = EdenUserManagement()

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
    response['message'] = f"Valid fields not found in request body {E}"
    response['status'] = 200
    return make_http_response(response) 

def throw_error(E):
    response = {}
    response['message'] = f"{E}"
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
            valid_fields = ['user_id', 'campaign_name']
            if check_field_validity(valid_fields, data):
                user_object = user_management_object.get_user_object(data['user_id'])
                if user_object is None:
                    return throw_error("User not found.")
                data['user_object'] = user_object
                pre_response = admax_object.create_advertisement_campaign(request, data)
                return make_http_response(pre_response)
            else:
                return throw_invalid_fields_error("")
        except Exception as E:
            return throw_error(E)
    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def create_advertisement_instance(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['campaign_id',
                             'user_id',
                            'target_topic_category_id',
                            'advertisement_tier',
                                   'text_content']
            if check_field_validity(valid_fields, data):
                pre_response = admax_object.create_advertisement_instance(request, data)
                return make_http_response(pre_response)
            else:
                return throw_invalid_fields_error([field for field in valid_fields if field not in data.keys()])
        except Exception as E:
            raise E
            return throw_error(E)
    else:
        return throw_http_method_not_supported_error()

@csrf_exempt
def get_campaign_id(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valid_fields = ['campaign_name', 'user_id']
            if check_field_validity(valid_fields, data):
                pre_response = admax_object.get_campaign_id(data['campaign_name'], data['user_id'])
                return make_http_response(pre_response)
            else:
                return throw_invalid_fields_error("")
        except Exception as E:
            return throw_error(E)
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
            return throw_error(E)
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
            return throw_error(E)
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
            return throw_error(E)
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
            return throw_error(E)
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
            return throw_error(E)
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
            return throw_error(E)
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
            return throw_error(E)
    else:
        return throw_http_method_not_supported_error()
    