import sublime
import sublime_plugin

import gzip
import json
import StringIO
import threading
import urllib2

class Settings:
  settings = sublime.load_settings(__name__ + '.sublime-settings')

  @staticmethod
  def init():
    Settings.settings.add_on_change(__name__ + '-reload', Settings.setup)
    Settings.setup()

  @staticmethod
  def setup():
    Settings.level                = Settings.settings.get('level', '')
    Settings.parser               = Settings.settings.get('parser', 'html5')
    Settings.timeout              = Settings.settings.get('timeout', 5)
    Settings.request_compression  = Settings.settings.get('request_compression', '')
    Settings.response_compression = Settings.settings.get('response_compression', '')
    Settings.error_icon           = Settings.settings.get('error_icon', 'circle')
    Settings.warning_icon         = Settings.settings.get('warning_icon', 'dot')

class Gzip:
  @staticmethod
  def compress(data, level = 9):
    string_buffer = StringIO.StringIO()
    gzip_file     = gzip.GzipFile(
      fileobj       = string_buffer,
      mode          = 'w',
      compresslevel = level
    )
    gzip_file.write(data)
    gzip_file.close()
    return string_buffer.getvalue()

  @staticmethod
  def decompress(data):
    return gzip.GzipFile( fileobj = StringIO.StringIO(data) ).read()
