
"""
MagadlalComExam package
"""

from importlib.metadata import version, PackageNotFoundError

try:
  __version__ = version("MagadlalComExam")
except PackageNotFoundError:
  __version__ = "0.0.0"

from .module import submit_solution

__all__ = ["submit_solution", "__version__"]
