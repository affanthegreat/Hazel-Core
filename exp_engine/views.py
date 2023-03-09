import json

from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate

from exp_engine.experience_engine import *


exp_engine_instance = EdenExperienceEngine()

@csrf_exempt
def initiate_exp_engine(request):
    if request.method == "POST":
        try:
            pre_response = exp_engine_instance.intitate(request)
            print(pre_response)
            return HttpResponse(
                content=json.dumps({"status": 200, "message": pre_response["issue"]})
            )
        except Exception as E:
             print(E)
             return HttpResponse(
                content=json.dumps({"status": 200, "message": "Cannot unload data."})
            )
