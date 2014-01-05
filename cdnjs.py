import sublime
import sublime_plugin
import threading
import json
import os
import time
try:
    from urllib.request import Request
    from urllib.request import urlopen
    from urllib.error import HTTPError
    from urllib.error import URLError
    from urllib.request import ProxyHandler
    from urllib.request import build_opener
    from urllib.request import install_opener
except:
    from urllib2 import Request
    from urllib2 import urlopen
    from urllib2 import HTTPError
    from urllib2 import URLError
    from urllib2 import ProxyHandler
    from urllib2 import build_opener
    from urllib2 import install_opener

settings = sublime.load_settings("cdnjs.sublime-settings")

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

class CdnjsFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        CdnjsApiCall(self.view, 30, True, True).start()

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
        self.wholeFile = args["wholeFile"]
        sublime.set_timeout(self.show_quickpanel, 10)

    def get_list(self):
        return [ [ x['name'], x.get('description','') ] for x in self.packages]

    def show_quickpanel(self):
        self.view.window().show_quick_panel(self.get_list(), self.callback)

    def callback(self, index):
        if index == -1:
            return

        pkg = self.packages[index]
        self.view.run_command('cdnjs_version_picker', {
            "package": pkg,
            "onlyURL": self.onlyURL,
            "wholeFile":self.wholeFile
        })


class CdnjsVersionPickerCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        self.package = args["package"]
        self.onlyURL = args["onlyURL"]
        self.wholeFile = args["wholeFile"]
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
            "wholeFile": self.wholeFile,
            "asset": asset
        })


class CdnjsFilePickerCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        self.package = args["package"]
        self.asset = args["asset"]
        self.onlyURL = args["onlyURL"]
        self.wholeFile = args["wholeFile"]
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
            "onlyURL": self.onlyURL,
            "wholeFile":self.wholeFile
        })


class CdnjsTagBuilder(sublime_plugin.TextCommand):
    CDN_URL = "//cdnjs.cloudflare.com/ajax/libs/"
    PATH_FORMAT = "%(name)s/%(version)s/%(filename)s"

    def run(self, edit, **args):
        self.package = args["package"]
        self.asset = args["asset"]
        self.file = args["file"]
        self.onlyURL = args["onlyURL"]
        self.wholeFile = args["wholeFile"]
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

        if self.wholeFile:
            self.view.run_command('cdnjs_download_file', {"file": path})
            return 
        elif self.onlyURL:
            tag = path
        else:
            tag = build_tag(path, markup, tag_type)

        self.view.run_command('cdnjs_place_text', {"tag": tag})


class CdnjsDownloadFileCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        sublime.status_message("Downloading file %s" % args["file"])
        CdnjsDownloadFile(self.view, 30, "http:"+args["file"]).start()

class CdnjsLoadingAnimation():
    def __init__(self,watch_thread):
        self.watch_thread = watch_thread
        sublime.set_timeout( lambda: self.run(0), 150 )

    def run(self, i):
        source = 'cached' if self.watch_thread.cachedResponse else 'latest'
        status_str = 'Fetching %s package list from cdn%s' % (source,'.' * (i%4))
        sublime.status_message(status_str)

        if not self.watch_thread.is_alive():
            sublime.status_message('')
            return

        sublime.set_timeout( lambda: self.run(i+1), 150 )

class CdnjsApiCall(threading.Thread):
    PACKAGES_URL = 'http://www.cdnjs.com/packages.json'

    def __init__(self, view, timeout, onlyURL=False, wholeFile=False):
        self.view = view
        self.timeout = timeout
        self.onlyURL = onlyURL
        self.wholeFile = wholeFile
        self.proxies = settings.get("proxies", {})
        self.cachedResponse = False
        self.cacheTime = settings.get("cache_ttl", 600)
        self.cacheDisabled = settings.get("cache_disabled", False)
        self.cacheFilePath = os.path.dirname(os.path.abspath(__file__))+'/package_list.cdncache'
        threading.Thread.__init__(self)
        CdnjsLoadingAnimation(self)

    def run(self):
        try:
            request = Request(self.PACKAGES_URL, headers={
                "User-Agent": "Sublime cdnjs"
            })

            #check the cache first
            result = self.get_cached_packagelist() if not self.cacheDisabled else None
            #not found, make the http request to fetch the packagelist
            if not result:
                proxy = ProxyHandler(self.proxies)
                opener = build_opener(proxy)
                install_opener(opener)
                http_file = urlopen(request, timeout=self.timeout)

                result = http_file.read().decode('utf-8')
                #set the cache
                self.set_packagelist_cache(result)

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
            "onlyURL": self.onlyURL,
            "wholeFile": self.wholeFile
        })

    def get_cached_packagelist(self):

        try:
            #try to open the cached file
            f = open(self.cacheFilePath, 'r')
            #create a dict
            packageList = json.loads(f.read())
            #and get the last save timestamp
            last_save = packageList.get('last_save')

            #check if the last save is older than the cacheTime
            if (int(time.time()) - last_save) > self.cacheTime:
                #missed cache, clear file
                os.remove(self.cacheFilePath)
                return None
            else:
                #hit cache, return cached data
                self.cachedResponse = True
                return json.dumps(packageList)

        except IOError as e:
            #there was no file found, no cache is set
            return None
        except Exception as e:
            print('Uncaught exception in cdnjs get cache: {}'.format(e))
            return None

    def set_packagelist_cache(self,packageListString):
        #read the package list to set a last_save stamp
        packageList = json.loads(packageListString)
        packageList.update({'last_save':int(time.time())})

        #write the value of the packagelist to a cache file
        f = open(self.cacheFilePath, 'w')
        f.write(json.dumps(packageList))


class CdnjsDownloadFile(threading.Thread):
    def __init__(self, view, timeout, file_path):
        self.view = view
        self.timeout = timeout
        self.file_path = file_path
        self.proxies = settings.get("proxies", {})
        threading.Thread.__init__(self)

    def run(self):
        try:
            request = Request(self.file_path, headers={
                "User-Agent": "Sublime cdnjs"
            })

            proxy = ProxyHandler(self.proxies)
            opener = build_opener(proxy)
            install_opener(opener)
            http_file = urlopen(request, timeout=self.timeout)

            result = http_file.read().decode('utf-8')

            self.data = result

            sublime.set_timeout(self.callback, 10)
        except HTTPError as e:
            error_str = '%s: HTTP error %s contacting API' % (__name__, str(e.code))
            sublime.error_message(error_str)
        except URLError as e:
            error_str = '%s: URL error %s contacting API' % (__name__, str(e.reason))
            sublime.error_message(error_str)

    def callback(self):
        self.view.run_command('cdnjs_place_text', {
            "tag":self.data
        })

