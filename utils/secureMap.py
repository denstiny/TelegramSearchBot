import threading
class secureMap():
    def __init__(self):
        self._lock = threading.Lock()
        self._map = {}

    def set(self,key,value):
        with self._lock:
            self._map[key] = value

    def get(self,key):
        with self._lock:
            return  self._map.get(key)

    def get_iter(self) -> dict:
        with self._lock:
            return dict(self._map)
