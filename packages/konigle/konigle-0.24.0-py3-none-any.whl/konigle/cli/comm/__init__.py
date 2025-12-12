"""
Communication CLI commands for the Konigle SDK.

This module provides CLI commands for managing email, SMS, WhatsApp,
and other communication channels.
"""

# Import base first to register the comm group
from . import base  # noqa

# Import commands to register them
from . import audiences  # noqa
from . import campaigns  # noqa
from . import contacts  # noqa
from . import email  # noqa