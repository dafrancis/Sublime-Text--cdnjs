import sublime
import threading

from .http import get


class CdnjsDownloadFile(threading.Thread):
    def __init__(self, view, timeout, file_path):
        self.settings = sublime.load_settings("cdnjs.sublime-settings")
        self.view = view
        self.timeout = timeout
        self.file_path = file_path
        self.proxies = self.settings.get("proxies", {})
        threading.Thread.__init__(self)

    def run(self):
        self.data = get(self.file_path, self.proxies, self.timeout)

        if self.data:
            sublime.set_timeout(self.callback, 10)

    def callback(self):
        self.view.run_command('cdnjs_place_text', {
            "tag":self.data
        })
