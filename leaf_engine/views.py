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
        valid_fields = ['text_content', 'leaf_type', 'auth_token', 'token']
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
    if request.method == "POST":
        try:    
            data = json.loads(request.body)
            page_number = data['page_number']
            response = {}
            response_status = ELM_object.get_user_public_leaves(request, int(page_number))
            if response_status == -101:
                response['message'] = 'Auth Error.'
                return response
            else:
                return JsonResponse(response_status, safe=False)
        except Exception as e:
            return make_response({'message': str(e)})
    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def get_leaves_view(request):
    if request.method == "POST":
        try:
            response = {}
            data = json.loads(request.body)
            response_status = ELM_object.get_leaves(request, data)
            if response_status == -101:
                response['message'] = 'Auth Error.'
                return response
            else:
                return JsonResponse(response_status, safe=False)
        except Exception as e:
            return make_response({'message': str(e)})
    else:
       return throw_http_method_not_supported_error()


@csrf_exempt
def get_user_private_leaves_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            page_number = data['page_number']
            response = {}
            response_status = ELM_object.get_user_private_leaves(request, int(page_number))
            if response_status == -101:
                response['message'] = 'Auth Error.'
                return response
            else:
               return JsonResponse(response_status, safe=False)
        except Exception as e:
            return make_response({'message': str(e)})
    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def delete_leaf_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id','auth_token','token']
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
        
        valid_fields = ['leaf_id', 'auth_token', 'token']
        if check_field_validity(valid_fields,data):
            response = ELM_object.like_leaf(request, data['leaf_id'])
            print(response)
            return make_response(response)
        else:
            return throw_invalid_fields_error()
    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def check_like(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id', 'user_id']
        if check_field_validity(valid_fields,data):
            response = ELM_object.check_like(data['leaf_id'], data['user_id'])
            return make_response(response)
        else:
            return throw_invalid_fields_error()
    else:
        return throw_http_method_not_supported_error()



@csrf_exempt
def check_dislike(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id', 'user_id']
        if check_field_validity(valid_fields,data):
            response = ELM_object.check_dislike(data['leaf_id'], data['user_id'])
            return make_response(response)
        else:
            return throw_invalid_fields_error()
    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def remove_like_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id', 'auth_token','token']
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
        valid_fields = ['leaf_id', 'comment_string', 'auth_token', 'token']
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
        valid_fields = ['leaf_id','auth_token', 'token']
        if check_field_validity(valid_fields,data):
           if ELM_object.check_leaf(data['leaf_id']):
                response = ELM_object.remove_comment(request, data['leaf_id'])
                return make_response(response)
           else:
               return make_response(-103)
        else:
           return throw_invalid_fields_error()
    else:
        return throw_http_method_not_supported_error()


@csrf_exempt
def remove_sub_comment_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id', 'comment_id', 'auth_token', 'token']
        if check_field_validity(valid_fields,data):
            response = ELM_object.remove_sub_comment(request, data['leaf_id'], data['comment_id'])
            return make_response(response)
        else:
           return throw_invalid_fields_error()
    else:
        return throw_http_method_not_supported_error()

@csrf_exempt
def get_all_likes(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            page_number = data['page_number']
            leaf_id = data['leaf_id']
            response = {}
            response = ELM_object.get_total_likes(leaf_id=leaf_id, page_number=int(page_number))
            return JsonResponse(response, safe=False)
        except Exception as e:
           return make_response({'message': str(e)})
    else:
       return throw_http_method_not_supported_error()


@csrf_exempt
def get_all_comments(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            page_number = data['page_number']
            leaf_id = data['leaf_id']
            response = ELM_object.get_total_comments(request, leaf_id,int(page_number))
            if response == -104:
               return HttpResponse(
                    content=json.dumps({"status": 200, "message": "No comments found."})
                )
            return JsonResponse(response, safe=False)
        except Exception as e:
           return make_response({'message': str(e)})
    else:
       return throw_http_method_not_supported_error()


@csrf_exempt
def get_all_dislikes(request):
    if request.method == "GET":
        data = json.loads(request.body)
        response = {}
        valid_fields = ['leaf_id','page_number', 'auth_token', 'token']
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
        valid_fields = ['leaf_id','auth_token', 'token']
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
        valid_fields = ['leaf_id','auth_token', 'token']
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
        valid_fields = ['leaf_id', 'comment_string','parent_comment_id','auth_token', 'token']
        if check_field_validity(valid_fields,data):
            if not ELM_object.check_leaf(data['leaf_id']):
                return throw_invalid_fields_error()
            
            if not ELM_object.check_comment(data['leaf_id'], data['parent_comment_id']):
                return throw_invalid_fields_error()
            
            object_creation_status = json.loads((add_comment_view(request).content).decode('utf-8'))
            if object_creation_status['message'] == -100:
                comment_id = object_creation_status['leaf_comment_id']
                parent_comment_id = data['parent_comment_id']
                response = ELM_object.add_sub_comment_db(comment_id,parent_comment_id)
                return make_response(response)
            else:
                return make_response(-103)
        else:
            return throw_invalid_fields_error()
    else:
       return throw_http_method_not_supported_error()



@csrf_exempt
def add_leaf_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        valid_fields = ['leaf_id','auth_token', 'token']
        if check_field_validity(valid_fields,data):
           response = ELM_object.create_view_object(request,data['leaf_id'])
           return make_response(response)
        else:
            return throw_invalid_fields_error()
    else:
       return throw_http_method_not_supported_error()
