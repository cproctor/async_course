from pathlib import Path
from random import random
from django.conf import settings

class TempFile:
    """A context manager providing one or more temporary files.
    """
    def __init__(self, n=1, delete_on_exit=True):
        self.n = n
        self.delete_on_exit = delete_on_exit
        self.paths = [self.get_path() for p in range(n)]

    def get_path(self):
       "Generates a path like '/tmp/f123123123'"
       return Path(settings.TMP_DIR) / ('f' + str(random())[2:])

    def __enter__(self):
        return self.path[0] if self.n == 1 else self.paths

    def __exit__(self, type, value, traceback):
        if self.delete_on_exit:
            for path in self.paths:
                if path.exists():
                    path.unlink()
