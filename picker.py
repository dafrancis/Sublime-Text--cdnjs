import sublime
import sublime_plugin


class CdnjsLibraryPickerCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        self.packages = args["packages"]
        self.onlyURL = args["onlyURL"]
        self.wholeFile = args["wholeFile"]
        sublime.set_timeout(self.show_quickpanel, 10)

    def get_list(self):
        package_list = []
        for x in self.packages:
            if not x.get('name'):
                x.update({'name': 'n/a'})
            if not x.get('description'):
                x.update({'description': 'n/a'})
            package_list.append([x['name'], x.get('description')])
        return package_list

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
        self.package = args.get("package", {})
        self.asset = args.get("asset", {})
        self.onlyURL = args.get("onlyURL", False)
        self.wholeFile = args.get("wholeFile", False)
        sublime.set_timeout(self.show_quickpanel, 10)

    def get_list(self):
        files = self.asset.get("files", [])
        return [f.get("name", '') for f in files]

    def show_quickpanel(self):
        self.view.window().show_quick_panel(self.get_list(), self.callback)

    def callback(self, index):
        if index == -1:
            return

        fileName = self.asset["files"][index]["name"]
        self.view.run_command('cdnjs_tag_builder', {
            "package": self.package,
            "asset": self.asset,
            "file": fileName,
            "onlyURL": self.onlyURL,
            "wholeFile": self.wholeFile
        })
