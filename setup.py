from distutils.core import setup
import py2exe

"""
    Example of py2exe for builing this app in *.exe
"""

DATA=[('ui/icons', ['C:\\Code/program/ui/icons/exit.png']),
      ('ui/icons', ['C:\\Code/program/ui/icons/options.png']),
      ('ui/icons', ['C:\\Code/program/ui/icons/other.png']),
      ('ui/icons', ['C:\\Code/program/ui/icons/tray.png']),
      ('ui/icons', ['C:\\Code/program/ui/icons/user.png']),
      ('ui', ['C:\\Code/program/ui/app.ico']),
      ('ui', ['C:\\Code/program/ui/options.ui']),
      ('ui', ['C:\\Code/program/ui/stats.ui']),
      ('imageformats',
       ['C:\\Python/Lib/site-packages/PyQt4/plugins/imageformats/qjpeg4.dll',
        'C:\\Python/Lib/site-packages/PyQt4/plugins/imageformats/qgif4.dll',
        'C:\\Python/Lib/site-packages/PyQt4/plugins/imageformats/qico4.dll'])
      ]

setup(
    windows=[{"script" : "client_gui.py"}],
    options={"py2exe" :
                {"includes" : ["sip", "PyQt4"],
                  "dll_excludes": ["MSVCP90.dll"],
                  'bundle_files': 1, 'compressed': True}
            },
    zipfile = None,
    data_files = DATA
 )
