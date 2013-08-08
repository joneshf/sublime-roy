import os
import subprocess

import sublime
import sublime_plugin


# This class name maps to the command name in the menu,
# where PascalCase and underscore_case are swapped.
class RoyCompile(sublime_plugin.TextCommand):

    ROY = 'roy'
    SETTINGS = sublime.load_settings('Roy.sublime-settings')
    WINDOW_NAME = 'roy_output'

    def run(self, edit):
        raw_text = self._text_to_compile()
        text = raw_text.encode('utf8')
        window = self.view.window()
        js, error = self._compile(text)
        self._write_to_window(window, edit, js, error)

    def _args(self):
        return self.ROY, '--stdio'

    def _compile(self, text):
        path = self._path()
        args = self._args()

        try:
            return self._execute_command(path, args, text)
        except OSError as e:
            sublime.status_message(str(e))
            return '', str(e)

    def _execute_command(self, path, args, text):
        proc = subprocess.Popen(args, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                env={'PATH': path})

        return proc.communicate(text)

    def _path(self):
        node = self.SETTINGS.get('node_path')
        roy = self.SETTINGS.get('roy_path')
        path = os.getenv('PATH')

        return os.pathsep.join(filter(None, (node, path, roy)))

    def _text_selected(self):
        return any(not selected.empty() for selected in self.view.sel())

    def _text_to_compile(self):
        if self._text_selected():
            region = self.view.sel()[0]
        else:
            region = sublime.Region(0, self.view.size())

        return self.view.substr(region)

    def _write_to_panel(self, panel, edit, text):
        panel.set_read_only(False)
        panel.insert(edit, 0, text)
        panel.sel().clear()
        panel.set_read_only(True)

    def _write_to_window(self, window, edit, js, error):
        panel = window.get_output_panel(self.WINDOW_NAME)
        panel.set_syntax_file('Packages/JavaScript/JavaScript.tmLanguage')

        raw_text = js if js != '' else error
        text = raw_text.decode('utf8')
        self._write_to_panel(panel, edit, text)

        window.run_command('show_panel',
                           {'panel': 'output.{0}'.format(self.WINDOW_NAME)})
