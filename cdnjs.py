import sublime
import sublime_plugin
import threading
import json
import os
try:
    from urllib.request import Request
    from urllib.request import urlopen
    from urllib.error import HTTPError
    from urllib.error import URLError
except:
    from urllib2 import Request
    from urllib2 import urlopen
    from urllib2 import HTTPError
    from urllib2 import URLError


TAGS = {
    ".html": {
        ".js": "<script src=\"%s\"></script>",
        ".css": "<link rel=\"stylesheet\" href=\"%s\">"
    },
    ".slim": {
        ".js": "script src=\"%s\"",
        ".css": "link rel=\"stylesheet\" href=\"%s\""
    },
    ".jade": {
        ".js": "script(src=\"%s\")",
        ".css": "link(rel=\"stylesheet\", href=\"%s\")"
    },
    ".haml": {
        ".js": "%%script{:src=>\"%s\"}",
        ".css": "%%link{:rel=>\"stylesheet\", :href=>\"%s\"}"
    }
}


def build_tag(url, extension, tagType):
    if extension not in TAGS:
        extension = ".html"
    return TAGS[extension][tagType] % url


class CdnjsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        CdnjsApiCall(self.view, 30).start()


class CdnjsUrlCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        CdnjsApiCall(self.view, 30, True).start()


class CdnjsPlaceTextCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        self.view.insert(edit, self.view.sel()[0].begin(), args["tag"])


class CdnjsLibraryPickerCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        self.packages = args["packages"]
        self.onlyURL = args["onlyURL"]
        sublime.set_timeout(self.show_quickpanel, 10)

    def get_list(self):
        return [[x['name'], x['description']] for x in self.packages]

    def show_quickpanel(self):
        self.view.window().show_quick_panel(self.get_list(), self.callback)

    def callback(self, index):
        if index == -1:
            return

        pkg = self.packages[index]
        self.view.run_command('cdnjs_version_picker', {
            "package": pkg,
            "onlyURL": self.onlyURL
        })


class CdnjsVersionPickerCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        self.package = args["package"]
        self.onlyURL = args["onlyURL"]
        sublime.set_timeout(self.show_quickpanel, 10)

    def get_list(self):
        assets = self.package["assets"]
        versions = [version["version"] for version in assets]
        return versions

    def show_quickpanel(self):
        self.view.window().show_quick_panel(self.get_list(), self.callback)

    def callback(self, index):
        if index == -1:
            return

        asset = self.package["assets"][index]
        self.view.run_command('cdnjs_file_picker', {
            "package": self.package,
            "onlyURL": self.onlyURL,
            "asset": asset
        })


class CdnjsFilePickerCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        self.package = args["package"]
        self.asset = args["asset"]
        self.onlyURL = args["onlyURL"]
        sublime.set_timeout(self.show_quickpanel, 10)

    def get_list(self):
        return self.asset["files"]

    def show_quickpanel(self):
        self.view.window().show_quick_panel(self.get_list(), self.callback)

    def callback(self, index):
        if index == -1:
            return

        fileName = self.asset["files"][index]
        self.view.run_command('cdnjs_tag_builder', {
            "package": self.package,
            "asset": self.asset,
            "file": fileName,
            "onlyURL": self.onlyURL
        })


class CdnjsTagBuilder(sublime_plugin.TextCommand):
    CDN_URL = "//cdnjs.cloudflare.com/ajax/libs/"
    PATH_FORMAT = "%(name)s/%(version)s/%(filename)s"

    def run(self, edit, **args):
        self.package = args["package"]
        self.asset = args["asset"]
        self.file = args["file"]
        self.onlyURL = args["onlyURL"]
        self.insert_tag()

    def get_path(self):
        path = self.PATH_FORMAT % {
            "name": self.package["name"],
            "version": self.asset["version"],
            "filename": self.file
        }

        return self.CDN_URL + path

    def insert_tag(self):
        path = self.get_path()
        markup = os.path.splitext(self.view.file_name() or "")[1]
        tag_type = os.path.splitext(path)[1]

        if self.onlyURL:
            tag = path
        else:
            tag = build_tag(path, markup, tag_type)

        self.view.run_command('cdnjs_place_text', {"tag": tag})


class CdnjsApiCall(threading.Thread):
    PACKAGES_URL = 'http://www.cdnjs.com/packages.json'

    def __init__(self, view, timeout, onlyURL=False):
        self.view = view
        self.timeout = timeout
        self.onlyURL = onlyURL
        threading.Thread.__init__(self)

    def run(self):
        try:
            request = Request(self.PACKAGES_URL, headers={
                "User-Agent": "Sublime cdnjs"
            })
            http_file = urlopen(request, timeout=self.timeout)
            result = http_file.read().decode('utf-8')

            self.packages = json.loads(result)['packages'][:-1]

            sublime.set_timeout(self.callback, 10)
        except HTTPError as e:
            error_str = '%s: HTTP error %s contacting API' % (__name__, str(e.code))
            sublime.error_message(error_str)
        except URLError as e:
            error_str = '%s: URL error %s contacting API' % (__name__, str(e.reason))
            sublime.error_message(error_str)

    def callback(self):
        self.view.run_command('cdnjs_library_picker', {
            "packages": self.packages,
            "onlyURL": self.onlyURL
        })
