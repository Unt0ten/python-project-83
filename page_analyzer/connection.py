import requests
from bs4 import BeautifulSoup


def get_seo(url):
    try:
        resp = requests.get(url)
    except Exception as ex:
        print('[INFO] URL broken!', ex)
        return 

    status = resp.status_code

    # if resp.raise_for_status():
    #     return

    soup = BeautifulSoup(resp.text, 'lxml')
    h1 = soup.h1
    if h1:
        h1 = h1.string

    title = soup.title
    if title:
        title = title.string

    description = None
    for meta in soup.find_all('meta'):
        if meta.get('name') == 'description':
            description = meta.get('content')

    return status, h1, title, description
