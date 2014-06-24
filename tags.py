import sublime_plugin

import os

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

class CdnjsTagBuilder(sublime_plugin.TextCommand):
    CDN_URL = "//cdnjs.cloudflare.com/ajax/libs/"
    PATH_FORMAT = "%(name)s/%(version)s/%(filename)s"

    def run(self, edit, **args):
        self.package = args.get("package", {})
        self.asset = args.get("asset", {})
        self.file = args.get("file", 'test.js')
        self.onlyURL = args.get("onlyURL", False)
        self.wholeFile = args.get("wholeFile", False)
        self.insert_tag()

    def get_path(self):
        path = self.PATH_FORMAT % {
            "name": self.package.get("name"),
            "version": self.asset.get("version"),
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
