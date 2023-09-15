def validate(data):
    return len(data) > 255


def normalize_url(url):
    if not url:
        return None
    return f'{str(url.scheme)}://' \
           f'{str(url.netloc.replace(":" + str(url.port), ""))}'


def make_dict(data1, data2, data3):
    data = []
    for id, name, date in zip(data1, data2, data3):
        data.append({"id": id, "name": name, "created_at": date})
    return data
