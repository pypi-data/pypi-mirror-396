#!/usr/bin/env python3
"""
happiness1 - A colorful gift box in your terminal 🎁
Spread joy this holiday season!
"""

import sys
import time

# ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
GOLD = '\033[33m'
BOLD = '\033[1m'
RESET = '\033[0m'


def get_gift():
    """Returns a colorful ASCII gift box."""
    
    gift = f"""
{YELLOW}{BOLD}        ★  ★  ★{RESET}
{GOLD}     ╔═══════════╗{RESET}
{GOLD}     ║{RED}  ░░░░░░░  {GOLD}║{RESET}
{RED}   ══╬═══{YELLOW}█{RED}═══╬══{RESET}
{RED}   ║ ║   {YELLOW}█{RED}   ║ ║{RESET}
{RED}   ║ ║   {YELLOW}█{RED}   ║ ║{RESET}
{RED}   ║ ║   {YELLOW}█{RED}   ║ ║{RESET}
{RED}   ║ ║   {YELLOW}█{RED}   ║ ║{RESET}
{RED}   ╚═╩═══{YELLOW}█{RED}═══╩═╝{RESET}
{GOLD}     ═══════════{RESET}

{GREEN}{BOLD}   ✦ Merry Christmas! ✦{RESET}
{WHITE}    Happy Holidays 🎄{RESET}
"""
    return gift


def get_gift_large():
    """Returns a larger, more elaborate gift box."""
    
    gift = f"""
{YELLOW}{BOLD}              ★ ✦ ★{RESET}
{YELLOW}             \\  |  /{RESET}
{YELLOW}              \\ | /{RESET}
{GOLD}        ╔═══════════════╗{RESET}
{GOLD}        ║{CYAN}  ~ ~ ~ ~ ~ ~  {GOLD}║{RESET}
{GOLD}        ║{CYAN} ~ ~ ~ ~ ~ ~ ~ {GOLD}║{RESET}
{RED}   ═════╬═══════{YELLOW}██{RED}═══════╬═════{RESET}
{RED}   ║    ║       {YELLOW}██{RED}       ║    ║{RESET}
{RED}   ║    ║       {YELLOW}██{RED}       ║    ║{RESET}
{RED}   ║    ║       {YELLOW}██{RED}       ║    ║{RESET}
{RED}   ║    ║       {YELLOW}██{RED}       ║    ║{RESET}
{RED}   ║    ║       {YELLOW}██{RED}       ║    ║{RESET}
{RED}   ║    ║       {YELLOW}██{RED}       ║    ║{RESET}
{RED}   ╚════╩═══════{YELLOW}██{RED}═══════╩════╝{RESET}
{GOLD}        ═════════════════{RESET}

{GREEN}{BOLD}      ✦ ❄ Merry Christmas! ❄ ✦{RESET}
{WHITE}        Wishing you joy and peace{RESET}
{CYAN}          Happy Holidays! 🎁{RESET}
"""
    return gift


def get_gift_animated():
    """Returns frames for an animated unwrapping effect."""
    
    # Frame 1: Wrapped gift
    frame1 = f"""
{GOLD}        ╔═══════════════╗{RESET}
{GOLD}        ║{CYAN}  ? ? ? ? ? ?  {GOLD}║{RESET}
{RED}   ═════╬═══════{YELLOW}██{RED}═══════╬═════{RESET}
{RED}   ║    ║       {YELLOW}██{RED}       ║    ║{RESET}
{RED}   ║    ║       {YELLOW}██{RED}       ║    ║{RESET}
{RED}   ║    ║       {YELLOW}██{RED}       ║    ║{RESET}
{RED}   ╚════╩═══════{YELLOW}██{RED}═══════╩════╝{RESET}

{WHITE}        Unwrapping...{RESET}
"""

    # Frame 2: Partially open
    frame2 = f"""
{GOLD}           ╔═════╗{RESET}
{GOLD}        ╔══╝     ╚══╗{RESET}
{GOLD}        ║           ║{RESET}
{RED}   ═════╬═══════════════╬═════{RESET}
{RED}   ║    ║             ║    ║{RESET}
{RED}   ║    ║             ║    ║{RESET}
{RED}   ║    ║             ║    ║{RESET}
{RED}   ╚════╩═════════════╩════╝{RESET}

{WHITE}        Almost there...{RESET}
"""

    # Frame 3: Message revealed
    frame3 = f"""
{YELLOW}{BOLD}        ★ ✦ ✦ ✦ ★{RESET}
{YELLOW}           \\|/{RESET}

{GREEN}{BOLD}   ╔═══════════════════════╗{RESET}
{GREEN}{BOLD}   ║                       ║{RESET}
{GREEN}{BOLD}   ║   {WHITE}MERRY CHRISTMAS!{GREEN}    ║{RESET}
{GREEN}{BOLD}   ║                       ║{RESET}
{GREEN}{BOLD}   ║   {CYAN}May your days be{GREEN}     ║{RESET}
{GREEN}{BOLD}   ║   {CYAN}merry and bright{GREEN}    ║{RESET}
{GREEN}{BOLD}   ║                       ║{RESET}
{GREEN}{BOLD}   ╚═══════════════════════╝{RESET}

{RED}      🎄 Happy Holidays! 🎄{RESET}
"""
    return [frame1, frame2, frame3]


def show_gift(large=False):
    """Display the gift box."""
    if large:
        print(get_gift_large())
    else:
        print(get_gift())


def show_animated():
    """Display animated unwrapping sequence."""
    frames = get_gift_animated()
    
    for i, frame in enumerate(frames):
        # Clear screen (works on most terminals)
        print('\033[2J\033[H', end='')
        print(frame)
        
        if i < len(frames) - 1:
            time.sleep(1.2)
    
    # Keep final frame visible
    time.sleep(0.5)


def show_help():
    """Display help message."""
    help_text = f"""
{GREEN}{BOLD}happiness1{RESET} - A colorful gift for your terminal 🎁

{WHITE}Usage:{RESET}
    happiness1              Show gift box
    happiness1 --large      Show larger gift box
    happiness1 --unwrap     Animated unwrapping!
    happiness1 --help       Show this help

{CYAN}Spread joy this holiday season!{RESET}
"""
    print(help_text)


def main():
    """Main entry point for CLI."""
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--large', '-l', '--big']:
            show_gift(large=True)
        elif arg in ['--unwrap', '-u', '--animate', '--open']:
            show_animated()
        elif arg in ['--help', '-h']:
            show_help()
        else:
            show_gift()
    else:
        show_gift()


if __name__ == "__main__":
    main()
