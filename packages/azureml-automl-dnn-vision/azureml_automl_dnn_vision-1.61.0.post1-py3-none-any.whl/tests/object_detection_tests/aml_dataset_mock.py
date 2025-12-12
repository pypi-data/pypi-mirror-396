import os
from shutil import copyfile


class DataflowStreamMock:

    def __init__(self, files_to_write) -> None:
        self._files_to_write = files_to_write

    def run_local(self):
        for file_path in self._files_to_write:
            copyfile(os.path.join(os.path.dirname(__file__),
                                  "../data/object_detection_data/images/000001679.png"),
                     file_path)
