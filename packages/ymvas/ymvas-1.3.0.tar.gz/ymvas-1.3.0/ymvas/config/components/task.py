

class Task:

    def __init__(self, src: str) -> None:
        self.src = src
        self._data = {}
    
    @property
    def data(self) -> dict:
        return self._data




