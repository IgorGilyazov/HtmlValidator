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

class ValidateHtmlCommand(sublime_plugin.TextCommand):
  def is_enabled(self):
    return self.view.size() > 0

  def run(self, edit):
    thread = ValidatorApi(
      self.view.substr( sublime.Region( 0, self.view.size() ) )
    )
    thread.start()
    self.handle_thread(thread)

  def handle_thread(self, thread, i = 0):
    if ( thread.is_alive() ):
      i = 0 if (i > 2) else i + 1
      self.view.set_status(
        __name__ + '-progress',
        '%s: (-_-)%s' % (__name__, 'z' * i)
      )
      sublime.set_timeout(
        lambda: self.handle_thread(thread, i),
        100
      )
      return

    self.view.erase_status(__name__ + '-progress')

    if (thread.state):
      self.handle_result(thread.result)

  def handle_result(self, result):
    try:
      result = json.loads(result)
    except ValueError as e:
      sublime.error_message(
        '%s: %s' % ( __name__, str(e) )
      )
      return

    global violations

    view_id             = self.view.id()
    violations[view_id] = {}
    error_lines         = []
    warning_lines       = []
    required_keys       = ('type', 'message', 'lastLine', 'extract')

    for message in result.get('messages', []):
      if all(k in message for k in required_keys):
        if ( message['lastLine'] not in violations[view_id] ):
          violations[view_id][ message['lastLine'] ] = []

        violations[view_id][ message['lastLine'] ].append(
          [
            '%s: %s' % ( message['type'], message['message'] ),
            '%s: %s' % ( message['lastLine'], message['extract'] )
          ]
        )

        if (message['type'] == 'error'):
          error_lines.append( message['lastLine'] )
        else:
          warning_lines.append( message['lastLine'] )

    # error mark overlaps warning mark.

    self.set_mark(
      __name__ + '-errors',
      error_lines,
      Settings.error_icon
    )
    self.set_mark(
      __name__ + '-warnings',
      [line for line in warning_lines if line not in error_lines],
      Settings.warning_icon
    )

  def set_mark(self, name, lines, icon):
    self.view.add_regions(
      name,
      [sublime.Region( self.view.text_point(line - 1, 0) ) for line in lines],
      name,
      icon,
      sublime.HIDDEN
    )

class ShowHtmlViolationsCommand(sublime_plugin.TextCommand):
  def is_enabled(self):
    global violations
    return self.view.id() in violations

  def run(self, edit):
    global violations

    view_id     = self.view.id()
    panel_items = []

    for v in violations[view_id].values():
      panel_items.extend(v)

    def on_done(selected_index):
      if (selected_index == -1):
        return

      self.view.run_command(
        'goto_line',
        {
          'line': panel_items[selected_index][1].split(':')[0]
        }
      )

    self.view.window().show_quick_panel(panel_items, on_done)

class FindHtmlViolationCommand(sublime_plugin.TextCommand):
  def is_enabled(self):
    global violations
    return self.view.id() in violations

  def run(self, edit, forward = True):
    view_id               = self.view.id()
    current_selected_line = self.view.rowcol( self.view.sel()[0].end() )[0] + 1
    lines                 = [
      line for line in violations[view_id] if line > current_selected_line
    ] if (forward) else [
      line for line in violations[view_id] if line < current_selected_line
    ]

    if ( len(lines) ):
      self.view.run_command(
        'goto_line',
        {
          'line': min(lines) if (forward) else max(lines)
        }
      )
