import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from leaf_engine.models import LeafType

from .leaf_management import EdenLeafManagement

ELM_object = EdenLeafManagement()


def make_response(map):
    return HttpResponse(content=json.dumps(map))

def check_field_validity(valid_fields, data):
    condition = True
    for field in valid_fields:
            if field not in data.keys():
                print(field)
                condition = False
    return condition

def throw_invalid_fields_error():
    response = {}
    response['message'] = "Valid fields not found in request body"
    response['status'] = 200
    return make_response(response)

def throw_http_method_not_supported_error():
     return HttpResponse(
            content=json.dumps({"status": 200, "message": "HTTP method is not supported."})
        )


@csrf_exempt
def create_leaf_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['text_content', 'leaf_type']
        if check_field_validity(valid_fields,data):
            if not data['text_content']:
                return make_response({"status":200, "message": "Text Content cannot be empty"})
            if data['leaf_type'] not in ['public', 'private']:
                return make_response({"status":200, "message": "Invalid leaf type"})
            response = ELM_object.create_leaf(request, data)
            return make_response(response)
        else:
           return throw_invalid_fields_error()
    else:
        return throw_http_method_not_supported_error()

@csrf_exempt
def get_user_public_leaves_view(request):
    if request.method == "GET":
        try:    
            page_number = request.GET.get('page_number')
            response = {}
            response_status = ELM_object.get_user_public_leaves(request, int(page_number))
            if response_status == -101:
                response['message'] = 'Auth Error.'
                return response
            else:
                return JsonResponse(response_status, safe=False)
        except Exception as e:
            return throw_invalid_fields_error()
    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def get_leaves_view(request):
    if request.method == "GET":
        try:
            response = {}
            user_id = request.GET.get('user_id')
            page_number = request.GET.get('page_number')
            response_status = ELM_object.get_leaves(request, user_id, int(page_number))
            if response_status == -101:
                response['message'] = 'Auth Error.'
                return response
            else:
                return JsonResponse(response_status, safe=False)
        except:
            return throw_invalid_fields_error()
    else:
       return throw_http_method_not_supported_error()


@csrf_exempt
def get_user_private_leaves_view(request):
    if request.method == "GET":
        try:
            page_number = request.GET.get('page_number')
            response = {}
            response_status = ELM_object.get_user_private_leaves(request, int(page_number))
            if response_status == -101:
                response['message'] = 'Auth Error.'
                return response
            else:
               return JsonResponse(response_status, safe=False)
        except Exception as e:
            return throw_invalid_fields_error()
    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def delete_leaf_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id']
        if check_field_validity(valid_fields,data):
            response = ELM_object.delete_leaf(request, data['leaf_id'])
            return make_response(response)
        else:
            return throw_invalid_fields_error()
    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def like_leaf_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id']
        if check_field_validity(valid_fields,data):
            response = ELM_object.like_leaf(request, data['leaf_id'])
            return make_response(response)
        else:
            return throw_invalid_fields_error()
    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def remove_like_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id']
        if check_field_validity(valid_fields,data):
            response = ELM_object.remove_like(request, data['leaf_id'])
            return make_response(response)
        else:
            return throw_invalid_fields_error()
    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def add_comment_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id', 'comment_string']
        if check_field_validity(valid_fields,data):
            response = ELM_object.add_comment(request, data['leaf_id'], data['comment_string'])
            return make_response(response)
        else:
           return throw_invalid_fields_error()
    else:
       return throw_http_method_not_supported_error()


@csrf_exempt
def remove_comment_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id']
        if check_field_validity(valid_fields,data):
            response = ELM_object.remove_comment(request, data['leaf_id'])
            return make_response(response)
        else:
           return throw_invalid_fields_error()
    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def remove_sub_comment_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id', 'comment_id']
        if check_field_validity(valid_fields,data):
            response = ELM_object.remove_sub_comment(request, data['leaf_id'], data['comment_id'])
            return make_response(response)
        else:
           return throw_invalid_fields_error()
    else:
        return throw_http_method_not_supported_error()

@csrf_exempt
def get_all_likes(request):
    if request.method == "GET":
        data = json.loads(request.body)
        response = {}
        valid_fields = ['leaf_id', "page_number"]
        if check_field_validity(valid_fields,data):
            response = ELM_object.get_total_likes(data['leaf_id'], data['page_number'])
            return JsonResponse(response, safe=False)
        else:
           return throw_invalid_fields_error()
    else:
       return throw_http_method_not_supported_error()


@csrf_exempt
def get_all_comments(request):
    if request.method == "GET":
        data = json.loads(request.body)
        valid_fields = ['leaf_id', 'page_number']
        if check_field_validity(valid_fields,data):
            response = ELM_object.get_total_comments(request, data['leaf_id'],data['page_number'])
            if response == -104:
               return HttpResponse(
                    content=json.dumps({"status": 200, "message": "No comments found."})
                )
            return JsonResponse(response, safe=False)
        else:
           return throw_invalid_fields_error()
    else:
       return throw_http_method_not_supported_error()


@csrf_exempt
def get_all_dislikes(request):
    if request.method == "GET":
        data = json.loads(request.body)
        response = {}
        valid_fields = ['leaf_id','page_number']
        if check_field_validity(valid_fields,data):
            response = ELM_object.get_total_dislikes(data['leaf_id'],data['page_number'])
            return JsonResponse(response, safe=False)
        else:
            return throw_invalid_fields_error()
    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def remove_dislike_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id']
        if check_field_validity(valid_fields,data):
            response = ELM_object.remove_dislike(request, data['leaf_id'])
            return make_response(response)
        else:
           return throw_invalid_fields_error()
    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def dislike_leaf_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id']
        if check_field_validity(valid_fields,data):
            response = ELM_object.dislike_leaf(request, data['leaf_id'])
            return make_response(response)
        else:
            return throw_invalid_fields_error()
    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def add_sub_comment_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id', 'comment_string','parent_comment_id']
        if check_field_validity(valid_fields,data):
            object_creation_status = json.loads((add_comment_view(request).content).decode('utf-8'))
            if object_creation_status['status_code'] == -100:
                comment_id = object_creation_status['leaf_comment_id']
                parent_comment_id = data['parent_comment_id']
                response = ELM_object.add_sub_comment_db(comment_id,parent_comment_id)
                return make_response(response)
        else:
            return throw_invalid_fields_error()
    else:
       return throw_http_method_not_supported_error()



@csrf_exempt
def add_leaf_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id']
        if check_field_validity(valid_fields,data):
           ELM_object.create_view_object(request,data['leaf_id'])
        else:
            return throw_invalid_fields_error()
    else:
       return throw_http_method_not_supported_error()
