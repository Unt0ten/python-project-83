from validators import url as validate_url
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
