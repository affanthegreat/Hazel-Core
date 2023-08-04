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

@csrf_exempt
def stream_users_by_topics_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            if 'topic_id' in data and 'page_number' in data:
                stream_data = communicator_object.stream_user_objects_by_topics(data['topic_id'], data['page_number'])
                return make_json_response(stream_data)
        except Exception as E:
            return make_http_response({"status": 200,
                                     "message": "Cannot unload data."})
    else:
        return make_http_response({"status": 200, "message": "HTTP method is not supported."})

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
                      print(e)
                      return make_http_response({"status": 200,
                                     "message": "Something went wrong while creating user topic object."})
        except Exception as E:
            return make_http_response({"status": 200,
                                     "message": "Cannot unload data."})
    else:
        return make_http_response({"status": 200, "message": "HTTP method is not supported."})


