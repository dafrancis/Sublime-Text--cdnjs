# Sublime Text - cdnjs

Like using http://www.cdnjs.com/? Like Sublime Text? Like plugins? Well this combines all three!

## How to use

1. Install plugin
2. In sublime `<ctrl|cmd> + <shift> + p`
3. Type in cdnjs (There will be an option to install a package)
4. Search and choose from the list of javascript libraries
5. ???
6. PROFIT!!!

## Proxy Settings

You can create a settings file: `"Sublime Text 3/Packages/User/cdnjs.sublime-settings"` and include the following setting to set use the plugin from behind a proxy:

    {
    	"proxies":{
    		"http":"http://proxy.com:80",
    		"https":"https://proxy.com:22"
    	}
    }

## Cache Settings

This plugin will cache a copy of the packages file from cdnjs. You can create a settings file: `"Sublime Text 3/Packages/User/cdnjs.sublime-settings"` and include the following settings to control the cache:

    {
        "cache_ttl": 600,
        "cache_disabled": false
    }

## Contributing

Pull requests are welcome, as long as they work on all supported operating systems (Windows, Mac, and Linux), and Sublime Text 2 and 3.

## Licence

Copyright (C) 2012 Dafydd Francis 

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
