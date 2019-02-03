import requests
from bs4 import BeautifulSoup

class Resource(object):
	def __init__(self, file: str, fetch_function):
		self.file = file
		self.fetch_function = fetch_function
		self.update()

	def get(self):
		return open(self.file).read()

	def file(self):
		return self.file

	def update(self):
		is_changed = False
		current_content = self._fetch()
		saved_content = None
		try:
			saved_content = open(self.file).read()
		except:
			pass
		if saved_content is None or saved_content != current_content:
			open(self.file, "wb").write(current_content)
			return True
		return False    

	def _fetch(self):
		return self.fetch_function()
		

def open_league_fetch():
    URL = "http://old1.club60sec.ru/calendar/6662/"
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, "html.parser")

    dropbox_href = None
    for link in soup.findAll('a'):
        link_text = link.get('href')
        if "dropbox" in link_text:
            dropbox_href = link_text
            break

    dropbox_href = "=".join(dropbox_href.split("=")[:-1] + ["1"])

    response = requests.get(dropbox_href)
    return response.content