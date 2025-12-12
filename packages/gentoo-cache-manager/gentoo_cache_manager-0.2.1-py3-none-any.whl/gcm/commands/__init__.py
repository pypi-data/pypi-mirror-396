from .clear import Clear
from .disable import Disable
from .enable import Enable
from .stats import Stats

COMMANDS = [
    Enable(),
    Disable(),
    Clear(),
    Stats(),
]
