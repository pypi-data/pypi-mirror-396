import platform

from importlib import metadata

package_version = metadata.version("cmsbx")

default_headers = {
    "lang": "python",
    "lang_version": platform.python_version(),
    "package_version": metadata.version("cmsbx"),
    "publisher": "cmsbx",
    "sdk_runtime": "python",
    "system": platform.system(),
}
