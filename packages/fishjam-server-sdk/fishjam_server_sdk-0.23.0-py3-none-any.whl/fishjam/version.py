from importlib.metadata import version

__version__ = version("fishjam-server-sdk")


def get_version():
    return __version__
