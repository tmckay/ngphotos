import multiprocessing as mp
from multiprocessing import Process, Queue
import os


class FileScanner:
    """Scans the filesystem and generates a file list"""
    def __init__(self, search_dir, extensions):
        print('init scanner')
        self.ctx = mp.get_context('spawn')
        self.queue = self.ctx.Queue(1)
        self.search_dir = search_dir
        self.extensions = extensions

    @staticmethod
    def _scan(search_dir, extensions, queue):
        """Scans a directory"""
        if not os.path.exists(search_dir) and not os.path.isdir(search_dir):
            return
        print(f'scanning {search_dir}')
        for item in os.listdir(search_dir):
            path = os.path.join(search_dir, item)
            if os.path.isfile(path):
                ext = os.path.splitext(path)[1].lower()
                print(f'found extension {ext}')
                if ext in extensions:
                    print(f'adding {path}')
                    queue.put(path)

    def start(self):
        """Starts separate process"""
        print('start scanner')
        self.process = self.ctx.Process(target=self._scan, args=(self.search_dir, self.extensions, self.queue,), daemon=True)
        self.process.start()

    def clear_queue(self):
        """Empties all items from the queue"""
        while not self.queue.empty():
            self.queue.get()

