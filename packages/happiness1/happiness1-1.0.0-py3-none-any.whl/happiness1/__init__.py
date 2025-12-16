"""
happiness1 - A colorful gift for your terminal 🎁
Spread joy this holiday season!

Usage:
    From terminal:
        $ happiness1
        $ happiness1 --large
        $ happiness1 --unwrap  (animated!)
    
    From Python:
        >>> import happiness1
        >>> happiness1.show_gift()
        >>> happiness1.show_animated()
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .main import (
    show_gift,
    show_animated,
    get_gift,
    get_gift_large,
    get_gift_animated,
    main
)

__all__ = [
    "show_gift",
    "show_animated", 
    "get_gift",
    "get_gift_large",
    "get_gift_animated",
    "main"
]

# Show the gift when imported!
show_gift()
