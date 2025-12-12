"""Initialization file for the testing_platform package."""
import os
import logging
from halo import Halo

RAGA_CONFIG_FILE = ".raga/config"
DEBUG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# Get the value of the DEBUG environment variable
debug_mode = os.environ.get('DEBUG')
spinner = Halo(text='Loading...', spinner='dots')

# Configure the logging format and level based on the DEBUG environment variable
if debug_mode:
    logging.basicConfig(
        format=DEBUG_FORMAT,
        level=logging.DEBUG
    )
    
if debug_mode:
    # Add a file handler to log messages to a file
    file_handler = logging.FileHandler('debug.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(DEBUG_FORMAT))

    # Add the file handler to the logger
    logger = logging.getLogger(__name__)
    logger.addHandler(file_handler)

from .filters import *
from .constants import *
from .test_session import *
from .dataset_creds import *
from .dataset import *
from .model import *
from .raga_schema import *
from ._tests import *
from .lightmetrics import *
from .inference import *
from .post_deployment_checks import *
from .model_executor_factory import ModelExecutorFactory