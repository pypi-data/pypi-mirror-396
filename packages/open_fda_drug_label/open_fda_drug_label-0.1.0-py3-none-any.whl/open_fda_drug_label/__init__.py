# read version from installed package
from importlib.metadata import version
__version__ = version("open_fda_drug_label")
from .open_fda_drug_label import make_drugs
from .api import Drug_Label_Client
from .drug import Drug
from .shelf import Shelf