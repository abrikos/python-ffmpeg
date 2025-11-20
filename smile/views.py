import json
import os.path
import subprocess
import time
import urllib.request

import requests
from django.conf import settings
from django.http import HttpResponse, JsonResponse

WEBHOOK_URL = settings.WEB_HOOK_URL

## Register webhook in tg bot
url = f"{settings.TELEGRAM_API_URL}/setWebhook?url={WEBHOOK_URL}/api/add-emoji"
response = requests.post(url)
print(WEBHOOK_URL, response.json())


def process_add_emoji(file_path):
    """Add emoji in video by ffmpeg"""
    tmp_file = os.path.join(settings.MEDIA_ROOT, "tmp" + os.path.basename(file_path))
    smile_file = os.getcwd() + "/assets/smile.jpeg"
    status = {"code": 200, "message": "OK"}
    try:
        subprocess.call(
            [
                "ffmpeg",
                "-y",
                "-i",
                file_path,
                "-i",
                smile_file,
                "-filter_complex",
                "overlay=(W-w)/2:(H-h)/2",
                "-c:a",
                "copy",
                tmp_file,
            ]
        )
        os.rename(tmp_file, file_path)
    except subprocess.CalledProcessError as e:
        status["code"] = 500
        status["message"] = str(e)
        status["tmp"] = tmp_file
    return status


def endpoint_add_emoji(request):
    """Endpoint controller"""
    if not os.path.exists(settings.MEDIA_ROOT):
        os.makedirs(settings.MEDIA_ROOT)

    response = {"status": 406, "url": "", "message": "not acceptable"}
    if request.method == "POST":
        file_name = str(time.time()) + ".mp4"
        if request.FILES and request.FILES["uploadedVideo"]:
            uploaded_file = request.FILES["uploadedVideo"]
            # file_name = uploaded_file.name
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)

            with open(file_path, "wb+") as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            response = process_add_emoji(file_path)
            if response["code"] == 200:
                response["url"] = os.path.join(settings.MEDIA_URL, file_name)
            return JsonResponse(response)
        else:
            message = json.loads(request.body.decode("utf-8"))
            # print(json.dumps(message, indent=4))
            chat_id = message["message"]["chat"]["id"]
            if message["message"] and "video" in message["message"]:
                # print(message['message']['video']['file_id'])
                tg_url = tg_get_file_url(message["message"]["video"]["file_id"])
                path = tg_download_file(file_name, tg_url)
                tg_response = process_add_emoji(path)
                if tg_response["code"] == 200:
                    tg_upload_file(chat_id, file=path)
                else:
                    tg_send_message(chat_id, "Error")
            return HttpResponse(200)
    else:
        return JsonResponse(response)


def tg_api(method, chat_id, files, message):
    """Request TG API"""
    data = {"chat_id": chat_id, "parse_mode": "HTML", "text": message}
    return requests.post(
        settings.TELEGRAM_API_URL + method, data=data, files=files, stream=True
    )


def tg_get_file_url(file_id):
    """Get bot file url by id"""
    file = requests.post(settings.TELEGRAM_API_URL + "getFile", {"file_id": file_id})
    text = json.loads(file.text)
    return settings.TELEGRAM_FILE_URL + text["result"]["file_path"]


def tg_download_file(file_name, url):
    """Download file from bot"""
    path = os.path.join(settings.MEDIA_ROOT, file_name)
    urllib.request.urlretrieve(url, path)
    return path


def tg_send_message(chat_id, message):
    """Send message to user"""
    return tg_api("sendMessage", chat_id, message=message, files=None)


def tg_upload_file(chat_id, file):
    """Upload file to bot"""
    files = {"document": open(file, "rb")}
    return tg_api("sendDocument", chat_id, files=files, message=None)
