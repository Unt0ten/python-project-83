from validators import url as validate_url
from requests.exceptions import RequestException


def validate_len(data):
    return len(data) > 255


def normalize_url(url):
    scheme = url.scheme
    netloc = url.netloc
    norm_url = f'{str(scheme)}://{str(netloc.replace(":" + str(url.port), ""))}'
    if not validate_url(norm_url):
        return False

    return norm_url


def validate_status_code(status_code):
    if status_code > 399:
        raise RequestException("Broken URL!")
    return status_code
