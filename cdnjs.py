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


class CdnjsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        CdnjsApiCall(self.view, 30).start()

class CdnjsPlaceTextCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        self.view.insert(edit, self.view.sel()[0].begin(), args["tag"])

class CdnjsApiCall(threading.Thread):
    CDN_URL = "//cdnjs.cloudflare.com/ajax/libs/"
    PACKAGES_URL = 'http://www.cdnjs.com/packages.json'

    def __init__(self, view, timeout):
        self.view = view
        self.timeout = timeout
        threading.Thread.__init__(self)

    def run(self):
        try:
            request = Request(self.PACKAGES_URL,
                headers={"User-Agent": "Sublime cdnjs"}
            )
            http_file = urlopen(request, timeout=self.timeout)
            result = http_file.read().decode('utf-8')

            self.packages = json.loads(result)['packages'][:-1]
            self.package_list = [[x['name'], x['description']] for x in self.packages]

            # show_quick_panel must execute on the main thread. This timeout will make it so
            sublime.set_timeout(self.show_quick_panel, 10)
        except HTTPError as e:
            error_str = '%s: HTTP error %s contacting API' % (__name__, str(e.code))
            sublime.error_message(error_str)
        except URLError as e:
            error_str = '%s: URL error %s contacting API' % (__name__, str(e.reason))
            sublime.error_message(error_str)

    def show_quick_panel(self):
        if not self.package_list:
            sublime.error_message(('%s: There are no packages available'))
            return
        self.view.window().show_quick_panel(self.package_list, self.insert_tag)

    def insert_tag(self, index):
        if index == -1:
            return
        pkg = self.packages[index]
        path = self.CDN_URL + "%(name)s/%(version)s/%(filename)s" % pkg

        markup = os.path.splitext(self.view.file_name() or "")[1]

        tag_type = os.path.splitext(pkg['filename'])[1]
        is_css = tag_type == '.css'

        if markup   == '.slim':
            if is_css:            tag = "link href=\"%s\"" % path
            else:                 tag = "script src=\"%s\"" % path
        elif markup == '.haml':
            if is_css:            tag = "%%link{:href=>\"%s\"}" % path
            else:                 tag = "%%script{:src=>\"%s\"}" % path
        elif markup == '.jade':
            if is_css:            tag = "link(href=\"%s\")" % path
            else:                 tag = "script(src=\"%s\")" % path
        else:
            if is_css:            tag = "<link href=\"%s\">" % path
            else:                 tag = "<script src=\"%s\"></script>" % path

        self.view.run_command('cdnjs_place_text', {"tag": tag})
