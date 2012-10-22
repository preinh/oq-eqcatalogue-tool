def name():
    return "My first plugin"

def description():
    return "This plugin has no real use."

def version():
    return "Version 0.1"

def qgisMinimumVersion():
    return "1.8"

def authorName():
    return "Giuseppe & Michele"

def classFactory(iface):
    from plugin import TestPlugin
    return TestPlugin(iface)