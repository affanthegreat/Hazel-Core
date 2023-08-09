import json


from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

from user_engine.communicator import EdenUserCommunicator
from user_engine.user_management import EdenUserManagement

communicator_object = EdenUserCommunicator()
user_control_object = EdenUserManagement()




def make_http_response(data):
    return HttpResponse(content=json.dumps(data))

def make_json_response(list_of_data):
    return JsonResponse(list_of_data)

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
def update_user_topics(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            if 'topic_id' in data and 'user_id' in data:
                try:
                    communicator_object.update_user_topics(data)
                    return make_http_response({"status":200, "message":"Successfully updated user topic object."})
                except Exception as e:
                      return make_http_response({"status": 200,
                                     "message": "Something went wrong while creating user topic object."})
        except Exception as E:
            return throw_invalid_fields_error()
    else:
        return throw_http_method_not_supported_error()


