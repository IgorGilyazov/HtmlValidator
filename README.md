HtmlValidator
=============

Summary
-------

HtmlValidator is a plugin for Sublime Text 2 that uses [Validator.nu](http://validator.nu/)
to validate HTML documents.
HtmlValidator uses gutter and quick panel to report HTML violations.

Installation
------------

### Without Git

Download the latest source from [GitHub](https://github.com/IgorGilyazov/HtmlValidator)
and copy the plugin folder to your Sublime Text "Packages" directory.

### With Git

Clone the repository in your Sublime Text "Packages" directory:

    git clone https://github.com/IgorGilyazov/HtmlValidator.git HtmlValidator

* * *

The "Packages" directory is located at:

- OS X:

        ~/Library/Application Support/Sublime Text 2/Packages/

- Linux:

        ~/.config/sublime-text-2/Packages/

- Windows:

        %APPDATA%/Sublime Text 2/Packages/

Settings
--------

For the latest information on what settings are available, check default settings file:
`Preferences -> Package Settings -> HtmlValidator -> Settings - Default`.

Key Bindings
------------

The plugin does not provide default keyboard shortcuts.
The reason for this is to prevent potential overlap problems with other installed plugins.
Key bindings can be added [manually](http://sublimetext.info/docs/en/customization/key_bindings.html).

Available commands:

- `"command": "validate_html"`
- `"command": "show_html_violations"`
- `"command": "find_html_violation", "args": { "forward": true }`
- `"command": "find_html_violation", "args": { "forward": false }`

Notes
-----

- Plugin commands can be accessed via "Tools" menu.
- Plugin settings can be accessed via "Preferences -> Package Settings" menu.
- If errors and warnings are present in the same line,
  only icon for error will be displayed in the gutter.
- Unlike quick panel, status bar length is not sufficient
  if multiple violations are present in the same line.

ToDo
----

- Sublime Text 3 support.
- `.sublime-commands` file.
- PEP-8 compliance.
