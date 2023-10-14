from validators import url as validate_url
from urllib.parse import urlparse
import requests


def validate_len(data):
    return len(data) > 255


def normalize_url(url):
    scheme = url.scheme
    netloc = url.netloc
    norm_url = f'{str(scheme)}://{str(netloc.replace(":" + str(url.port), ""))}'
    if not validate_url(norm_url):
        return False

    return norm_url


def get_response(url):
    try:
        resp = requests.get(url)
        return resp

    except Exception as ex:
        print(f'[INFO] {ex}')
        return None


def check_url_errors(url):
    if not url:
        messages = 'URL обязателен', 'warning'
        return messages

    norm_url = normalize_url(urlparse(url))

    if not norm_url:
        messages = 'Некорректный URL', 'warning'
        return messages

    if validate_len(url):
        messages = 'URL превышает 255 символов', 'warning'
        return messages
