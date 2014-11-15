__author__ = 'Rik Verbeek'

#!/usr/bin/env python
# Encoding		: utf-8
# File			: ShowInfo.py
# Version		: 0.0
# Author		: Rik Verbeek


class ShowInfo:

    def __init__(self):
        pass

    def show(self, text):
        print("\t %s" % text)

    def info(self, text):
        print("[I] %s" % text)

    def custom(self, text, identifier):
        print("[%c] %s" % (identifier, text))

    def debug(self, text):
        print("[D] %s" % text)

    def warning(self, text):
        print("[W] %s" % text)

    def error(self, text):
        print("[E] %s" % text)

    def fatal(self, text):
        print("[F] %s" % text)

