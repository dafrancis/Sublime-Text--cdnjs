import sublime
import sublime_plugin
import urllib2
import threading
import json


class CdnjsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        CdnjsApiCall(self.view, edit, 30).start()


class CdnjsApiCall(threading.Thread):
    def __init__(self, view, edit, timeout):
        self.view = view
        self.edit = edit
        self.timeout = timeout
        threading.Thread.__init__(self)

    def run(self):
        try:
            request = urllib2.Request('http://www.cdnjs.com/packages.json',
                headers={"User-Agent": "Sublime cdnjs"}
            )
            http_file = urllib2.urlopen(request, timeout=self.timeout)
            result = http_file.read()

            self.packages = json.loads(result)['packages'][:-1]
            package_list = [[x['name'], x['description']] for x in self.packages]

            def show_quick_panel():
                if not package_list:
                    sublime.error_message(('%s: There are no packages available'))
                    return
                self.view.window().show_quick_panel(package_list, self.insert_tag)

            # show_quick_panel must execute on the main thread. This timeout will make it so
            sublime.set_timeout(show_quick_panel, 10)
        except (urllib2.HTTPError) as (e):
            sublime.error_message('%s: HTTP error %s contacting API' % (__name__, str(e.code)))
        except (urllib2.URLError) as (e):
            sublime.error_message('%s: URL error %s contacting API' % (__name__, str(e.reason)))

    def insert_tag(self, index):
        if index == -1:
            return
        pkg = self.packages[index]
        cdn_url = "//cdnjs.cloudflare.com/ajax/libs/"
        path = "%s/%s/%s" % (pkg['name'], pkg['version'], pkg['filename'])
        tag = "<script src=\"%s%s\"></script>" % (cdn_url, path)
        self.view.insert(self.edit, self.view.sel()[0].begin(), tag)
