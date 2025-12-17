# Import the build command to register it
from .build import BuildCommand  # noqa: F401
from .dist import BuildDistCommand  # noqa: F401
from .test import BuildTestCommand  # noqa: F401
