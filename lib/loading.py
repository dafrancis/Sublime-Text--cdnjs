import sublime

class CdnjsLoadingAnimation(object):

    """The dot dot dot animation in the status bar."""

    def __init__(self, watch_thread):
        """Initialise."""
        self.watch_thread = watch_thread
        sublime.set_timeout(lambda: self.run(0), 150)

    def run(self, i):
        """Run the animation."""
        source = 'cached' if self.watch_thread.cachedResponse else 'latest'
        status_str = 'Fetching %s package list from cdn%s' % (source, '.' * (i % 4))
        sublime.status_message(status_str)

        if not self.watch_thread.is_alive():
            sublime.status_message('')
            return

        sublime.set_timeout(lambda: self.run(i + 1), 150)


