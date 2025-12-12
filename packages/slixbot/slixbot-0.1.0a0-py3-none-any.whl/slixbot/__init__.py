"""
.. include:: ../README.md
   :start-line: 1

"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("slixbot")
except PackageNotFoundError:
    # package is not installed
    __version__ = "dev"


from .client import Client
from .message import Contact, Message, Participant

__all__ = ("Client", "Message", "Contact", "Participant")
