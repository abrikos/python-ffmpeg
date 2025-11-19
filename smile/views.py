from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def add_emoji(request):
    print(request.method)
    if request.method == 'POST':
        print('POST', request.FILES['uploadedVideo'])
        return HttpResponse('zzzz222')
    else:
        print('GET')
        return HttpResponse('upload')
