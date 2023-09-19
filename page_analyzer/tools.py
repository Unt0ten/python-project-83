from validators import url as validate_url
from requests.exceptions import RequestException

def validate_len(data):
    return len(data) > 255


def normalize_url(url):
    scheme = url.scheme
    netloc = url.netloc
    norm_url = f'{str(scheme)}://' \
               f'{str(netloc.replace(":" + str(url.port), ""))}'
    if not validate_url(norm_url):
        return False

    return norm_url


def make_dict_urls(data):
    result = []
    for row in data:
        result.append({"id": row[0], "name": row[1], "created_at": row[2]})

    return result


def make_dict_checks(data):
    result = []
    for row in data:
        result.append(
            {"id": row[0], "status": row[2], "h1": row[3], "title": row[4],
             "desc": row[5], "created_at": row[6]}
            )

    return result

def validate_status_code(status_code):
    if status_code == 500:
        raise RequestException("Broken URL!")
    return status_code
