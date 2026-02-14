"""POC Manager Application"""

import warnings

# Suppress external dependency warnings that don't affect functionality
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="passlib.utils"
)
warnings.filterwarnings("ignore", message=".*'crypt'.*deprecated.*")
