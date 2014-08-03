import sublime
import sublime_plugin

st_version = 2

if sublime.version() == '':
    st_version = 3
    print('CDNJS: Please upgrade to Sublime Text 3 build 3012 or newer')

elif int(sublime.version()) > 3000:
    st_version = 3

if st_version == 3:
    from .lib.api import CdnjsApiCall
    from .lib.download import CdnjsDownloadFile
    from .lib.search import CdnjsSearchCall
else:
    from lib.search import CdnjsSearchCall
    from lib.api import CdnjsApiCall
    from lib.download import CdnjsDownloadFile


class CdnjsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        CdnjsApiCall(self.view, 30).start()

class CdnjsFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        CdnjsApiCall(self.view, 30, True, True).start()

class CdnjsUrlCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        CdnjsApiCall(self.view, 30, True).start()

class CdnjsPlaceTextCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        self.view.insert(edit, self.view.sel()[0].begin(), args["tag"])

class CdnjsDownloadFileCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        sublime.status_message("Downloading file %s" % args["file"])
        CdnjsDownloadFile(self.view, 30, "http:"+args["file"]).start()

class CdnjsSearchCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        CdnjsSearchCall(self.view, 30).start()