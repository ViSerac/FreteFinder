from cx_Freeze import setup, Executable
import sys

build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

base = None

if sys.platform == "win32":
    base = "Win32GUI"


executables = [Executable("fretefinder.py", base=base)]

packages = ["idna"]
options = {
    'build_exe': {

        'packages':packages,
    },

}

setup(
    name = "Frete Finder",
    options = options,
    version = "1.4",
    description = 'Buscador de Fretes',
    executables = executables
)
