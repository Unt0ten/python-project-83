from bs4 import BeautifulSoup


class PHtml:
    def __init__(self, resp):
        self.soup = BeautifulSoup(resp.text, 'lxml')

    def get_h1(self):
        h1 = self.soup.h1
        if h1:
            h1 = h1.string
        return h1

    def get_title(self):
        title = self.soup.title
        if title:
            title = title.string
        return title

    def get_description(self):
        description = None
        for meta in self.soup.find_all('meta'):
            if meta.get('name') == 'description':
                description = meta.get('content')
        return description
