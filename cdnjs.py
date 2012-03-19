import sublime
import sublime_plugin
import urllib2
import threading
import json


class CdnjsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.edit = edit
        self.packages = CdnjsApiCall(30).run()
        package_list = map(lambda x: [x['name'], x['description']], self.packages)
        self.view.window().show_quick_panel(package_list, self.insert_tag)

    def insert_tag(self, index):
        if index == -1:
            return
        pkg = self.packages[index]
        cdn_url = "http://cdnjs.cloudflare.com/ajax/libs/"
        path = "%s/%s/%s" % (pkg['name'], pkg['version'], pkg['filename'])
        tag = "<script src=\"%s%s\"></script>" % (cdn_url, path)
        self.view.insert(self.edit, self.view.sel()[0].begin(), tag)


class CdnjsApiCall(threading.Thread):
    def __init__(self, timeout):
        self.timeout = timeout
        threading.Thread.__init__(self)

    def run(self):
        try:
            request = urllib2.Request('http://www.cdnjs.com/packages.json',
                headers={"User-Agent": "Sublime cdnjs"}
            )
            http_file = urllib2.urlopen(request, timeout=self.timeout)
            result = http_file.read()
            return json.loads(result)['packages'][:-1]

        except (urllib2.HTTPError) as (e):
            err = '%s: HTTP error %s contacting API' % (__name__, str(e.code))
        except (urllib2.URLError) as (e):
            err = '%s: URL error %s contacting API' % (__name__, str(e.reason))

        sublime.error_message(err)
        return False
