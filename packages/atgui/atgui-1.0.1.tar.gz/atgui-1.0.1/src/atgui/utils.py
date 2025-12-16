import colorama
import platform
if (platform.system() != "Windows"): # Import these for Linux to access Keyboard Presses
    import termios
    import tty
    import sys

def color_ret(color: str, type: str):
        if color == "white":
            if type == "fore":
                return colorama.Fore.WHITE
            elif type == "back":
                return colorama.Back.WHITE
            
        if color == "red":
            if type == "fore":
                return colorama.Fore.RED
            elif type == "back":
                return colorama.Back.RED
            
        if color == "yellow":
            if type == "fore":
                return colorama.Fore.YELLOW
            elif type == "back":
                return colorama.Back.YELLOW
            
        if color == "blue":
            if type == "fore":
                return colorama.Fore.BLUE
            elif type == "back":
                return colorama.Back.BLUE
            
        if color == "cyan":
            if type == "fore":
                return colorama.Fore.CYAN
            elif type == "back":
                return colorama.Back.CYAN
                
        return ""

def linux_get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch1 = sys.stdin.read(1)
            if ch1 == '\x1b':  # Escape sequence
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A':
                        return 'up'
                    elif ch3 == 'B':
                        return 'down'
                    elif ch3 == 'C':
                        return 'right'
                    elif ch3 == 'D':
                        return 'left'
            elif ch1 == '\r' or ch1 == '\n':
                return 'enter'
            elif ch1 == '\x03':
                return 'ctrl_c'
            elif ch1 == '\x1b':
                return 'esc'
            else:
                return ch1
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)