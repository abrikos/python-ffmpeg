import os.path
from wsgiref.util import FileWrapper

from django.conf import settings
from django.http import HttpResponse, JsonResponse
import subprocess

from celery import shared_task
from urllib.parse import urljoin


@shared_task
def process_add_emoji(file_path, tmp_file):
    smile_file = os.getcwd() + '/assets/smile.jpeg'
    status = {'code': 200, 'message': 'OK'}
    try:
        subprocess.run(['ffmpeg', '-y', '-i', file_path, '-i', smile_file, '-filter_complex', 'overlay=(W-w)/2:(H-h)/2', '-c:a', 'copy', tmp_file])
    except subprocess.CalledProcessError as e:
        status['code'] = 500
        status['message'] = str(e)
    return status


def add_emoji(request):
    response = {
        'status': 406,
        'url': '',
        'message': 'not acceptable'
    }
    if request.method == 'POST' and request.FILES['uploadedVideo']:
        uploaded_file = request.FILES['uploadedVideo']
        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        tmp_file = urljoin(settings.MEDIA_ROOT, 'tmp' + uploaded_file.name)

        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)

        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        response = process_add_emoji(file_path, tmp_file)
        if response['code'] == 200:
            try:
                os.rename(tmp_file, file_path)
                response['url'] = os.path.join(settings.MEDIA_URL, uploaded_file.name)
            except FileNotFoundError as e:
                response['code'] = 500
                response['message'] = 'Processing file error'

        return JsonResponse(response)

    else:
        return JsonResponse(response)
