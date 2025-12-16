def main(string , colors):
    if len(colors) == 2:
        if colors["color_mode"] == None or colors["color"] == None:
            print("List does not have a color_mode or color argument.")
            return 407
        match colors["color_mode"]:
            case 0: #off
                return string
            case 1: #on
                return f"\033[{colors["color"]}m {string}\033[0m"
    print("The colors list must have only 2 argument")
    return 402