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

class ValidatorApi(threading.Thread):
  validator = 'http://validator.nu/'

  def __init__(self, data):
    self.data         = data
    self.query_string = 'out=json&parser=' + Settings.parser
    if ( len(Settings.level) ):
      self.query_string += '&level=' + Settings.level
    self.state        = None
    threading.Thread.__init__(self)

  def run(self):
    data    = self.data
    headers = {
      'Content-Type': 'text/html',
      'User-Agent': 'Sublime Text %s plugin' % __name__
    }

    if (Settings.request_compression == 'gzip'):
      headers['Content-Encoding'] = 'gzip'
      data                        = Gzip.compress(data)

    if (Settings.response_compression == 'gzip'):
      headers['Accept-Encoding'] = 'gzip'

    headers['Content-Length'] = len(data)

    try:
      response    = urllib2.urlopen(
        urllib2.Request(
          ValidatorApi.validator + '?' + self.query_string, data, headers
        ),
        timeout = Settings.timeout
      )
      self.result = response.read()
    except (urllib2.HTTPError, urllib2.URLError) as e:
      self.state = False
      sublime.error_message(
        '%s: %s' % ( __name__, str(e) )
      )
      return

    if (response.info().getheader('Content-Encoding', '').lower() == 'gzip'):
      self.result = Gzip.decompress(self.result)

    self.state = True
