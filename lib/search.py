import sublime
import json
import threading
from .http import get

class CdnjsSearchCall(threading.Thread):
    """
    A command that prompts the user to enter search query text.
    """

    def __init__(self, view, timeout=10):
        self.view = view
        self.timeout = timeout
        self.types = [
            ['<script> tag','Import the script tag'],
            ['URL','Import only the URL'],
            ['file','Import the entire file']
        ]
        self.settings = sublime.load_settings("cdnjs.sublime-settings")
        self.proxies = self.settings.get("proxies", {})
        threading.Thread.__init__(self)

    def run(self):
        self.show_type_quickpanel()

    def show_type_quickpanel(self):
        self.view.window().show_quick_panel(self.types, self.callback)

    def callback(self, index):
        if index == -1:
            return

        self.onlyURL = False
        self.wholeFile = False
        if self.types[index][0] == 'file':
            self.wholeFile = True
        elif self.types[index][0] == 'URL':
            self.onlyURL = True

        def show_input_panel():
            self.view.window().show_input_panel(
                'Enter a search query',
                '',
                self.on_done,
                self.on_change,
                self.on_cancel
                )
        sublime.set_timeout(show_input_panel, self.timeout)

    def search(self,query):
        fullUrl = "{}{}{}".format(self.settings.get('domain', 'http://api.cdnjs.com'),
                            self.settings.get('path',
                                         '/libraries?'
                                         'fields=assets,'
                                         'description&search='),
                            query)
        result = get(fullUrl, self.proxies, self.timeout)
        return json.loads(result)['results'][:-1]

    def on_done(self, text):
        self.packages = self.search(text)
        self.view.run_command('cdnjs_library_picker', {
            "packages": self.packages,
            "onlyURL": self.onlyURL,
            "wholeFile": self.wholeFile
        })

    def on_change(self,**args):
        pass

    def on_cancel(self,**args):
        pass
