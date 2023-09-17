def validate(data):
    return len(data) > 255


def normalize_url(url):
    scheme = url.scheme
    netloc = url.netloc
    if not scheme or not netloc:
        return False

    return f'{str(scheme)}://' \
           f'{str(netloc.replace(":" + str(url.port), ""))}'


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
