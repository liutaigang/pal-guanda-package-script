import json

class Cache:
    def __init__(self):
        self.cache_path = "./cache.json"

    def save(self, data):
        with open(self.cache_path, 'r') as f:
            exsit = json.load(f)
            if type(exsit) is dict:
                data.update(exsit)
            with open(self.cache_path, 'w') as f:
                json.dump(data, f, indent = 4)

    def get(self):
        try:
            with open(self.cache_path, 'r') as f:
                data = json.load(f)
                return data
        except:
            with open(self.cache_path, 'w') as f:
                json.dump({}, f,)
            return {}
        