from .utils import color_ret

def equalsbar_g(title: str, description: str = "", width: int = 16, color: str = "white", options: list = [], selected_option: int = -1):
        try:
            width_int = int(width)
            padding = width_int // 2
            t_bar = ("=" * padding) + " " + title + " " + ("=" * padding) # Top bar
            d_bar = ("=" * (padding + 1)) + ("=" * len(title)) + ("=" * (padding + 1)) # Down bar

            print_buffer = ""
            print_buffer += f"{color_ret(color, "fore")}{t_bar}\n"
            
            if description and len(description):
                print_buffer += f"{color_ret(color, "fore")}- {description}\n"
                

            for i, option in enumerate(options):
                print_buffer += f"{color_ret(color, "fore")}{"->" if i + 1 == selected_option else ">"} {i + 1}. {"\033[4m" if i + 1 == selected_option else "" }{option} {f"[Selected]" if i + 1 == selected_option else "" }\033[0m\n"
            
            print_buffer += f"{color_ret(color, "fore")}{d_bar}"

            print(print_buffer)
        except Exception as e:
            return False, e

guis = {
    "equalsbar": {
        "function": equalsbar_g,
        "menu": True,
        "delay": 0.1
    },
    
}