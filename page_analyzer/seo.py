from bs4 import BeautifulSoup


def get_page_data(resp):
    status = resp.status_code
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

    return {
        'status': status, 'h1': h1, 'title': title, 'description': description
    }
