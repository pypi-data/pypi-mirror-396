from .base import *


# https://jwodder.github.io/kbits/posts/pypkg-data/
# https://copdips.com/2022/09/adding-data-files-to-python-package-with-setup-py.html
class FakeAgentClass:

    def __init__(self):
        # self.folder = '../data'
        self.folder = '../json'
        self.filename = 'browsers.json'

    def __repr__(self): 
        return """Web Agents ['random','chrome','opera','firefox','internetexplorer','safari']"""

    @property
    def _load(self):
        # loading data file
        DB_PATH = os.path.join(os.path.dirname(__file__), self.folder)
        with open(DB_PATH + f"/{self.filename}", 'r') as file:
            json_data = file.read()
        json_data = json.loads(json_data)['browsers']
        return json_data

    def _get(self, name:str=None):
        # Browser Agent
        json_data = self._load
        browser_list = list(json_data.keys())
        if name not in browser_list:
            return None
        # Return Item
        items = json_data[name]
        return  json_data[name][random.randint(1, len(items)-1)]

    @property
    def chrome(self):
        return self._get('chrome')

    @property
    def opera(self):
        return self._get('opera')

    @property
    def firefox(self):
        return self._get('firefox')

    @property
    def safari(self):
        return self._get('safari')

    @property
    def internetexplorer(self):
        return self._get('internetexplorer')

    @property
    def random(self):
        json_data = self._load
        names = list(json_data.keys())
        name  = names[random.randint(1, len(names)-1)]
        return self._get(name)

FakeAgent = FakeAgentClass()
