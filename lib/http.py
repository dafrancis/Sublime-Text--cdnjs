import sublime
import zlib

try:
    from urllib.request import Request
    from urllib.request import urlopen
    from urllib.error import HTTPError
    from urllib.error import URLError
    from urllib.request import ProxyHandler
    from urllib.request import build_opener
    from urllib.request import install_opener
except ImportError:
    from urllib2 import Request
    from urllib2 import urlopen
    from urllib2 import HTTPError
    from urllib2 import URLError
    from urllib2 import ProxyHandler
    from urllib2 import build_opener
    from urllib2 import install_opener


def get(path, proxies, timeout):
    try:
        request = Request(path, headers={
            "User-Agent": "Sublime cdnjs",
            "Accept-Encoding": "gzip,deflate,sdch"
        })

        proxy = ProxyHandler(proxies)
        opener = build_opener(proxy)
        install_opener(opener)
        http_file = urlopen(request, timeout=timeout)

        result = http_file.read()

        # decompress response body when content-encoding is gzip
        respInfo = http_file.info()
        if (("Content-Encoding" in respInfo) and (respInfo['Content-Encoding'] == "gzip")):
            result = zlib.decompress(result, 16+zlib.MAX_WBITS);

        return result.decode('utf-8')
    except HTTPError as e:
        error_str = '%s: HTTP error %s contacting API' % (__name__, str(e.code))
        sublime.error_message(error_str)
    except URLError as e:
        error_str = '%s: URL error %s contacting API' % (__name__, str(e.reason))
        sublime.error_message(error_str)
    return ''
