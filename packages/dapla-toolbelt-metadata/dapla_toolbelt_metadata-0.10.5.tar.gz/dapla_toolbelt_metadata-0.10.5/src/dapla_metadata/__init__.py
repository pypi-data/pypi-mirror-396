"""Tools and clients for working with the Dapla Metadata system."""

import sys
import warnings

warnings.filterwarnings(
    "ignore",
    message="As the c extension couldn't be imported, `google-crc32c` is using a pure python implementation that is significantly slower.",
)

import datadoc_model.all_optional.model as datadoc_model

from . import dapla
from . import datasets
from . import standards

if sys.version_info >= (3, 11):
    # dapla_auth_client only supports Python >=3.11
    # We must still support 3.10 for now, but variable definitions never runs on 3.10
    from . import variable_definitions
