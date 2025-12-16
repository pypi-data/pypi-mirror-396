import time
def main(string, efects):
    if len(efects) == 2:
        if efects["efect_mode"] == None or efects["efect"] == None:
            print("List does not have a efect_mode or efect argument.")
            return 307
        match efects["efect_mode"]:
            case 0: #off
                print(string)
                return 0
            case 1: #on
                efect = efects["efect"] if (efects["efect"]).count(":") == 0 else (efects["efect"])[0:(efects["efect"]).find(":")]
                string_list_and_color = string.split()
                sch = 0
                string_list_not_color = []
                for e in string_list_and_color:
                        if sch == len(string_list_and_color) - 1:
                            break
                        elif sch == 0:
                            sch += 1
                        else:
                            string_list_not_color.append(e)
                            sch += 1
                del sch , e
                match efect:
                    case "reverse_work":
                        reverse_string_list_not_color = []
                        for i in range(0, len(string_list_not_color)):
                            reverse_string_list_not_color.append(string_list_not_color[len(string_list_not_color) - i - 1])
                        print(string_list_and_color[0] + " " + " ".join(reverse_string_list_not_color) + " " + string_list_and_color[(len(string_list_and_color))-1])
                        return 0
                    case "time_work":
                        interval = float(((efects["efect"]).replace("time_work:" , "")).replace(" ", ""))
                        string_list = string.split(" ")
                        for i in string_list:
                            print(i , end=" ")
                            time.sleep(interval)
                        return 0
                    case "time_letters":
                        interval = float(((efects["efect"]).replace("time_letters:" , "")).replace(" ", ""))
                        print(string_list)
                        for m in string_list:
                            for i in m:
                                print(i , end="" , flush = True)
                                time.sleep(interval)
                            print(" " , end="" , flush = True)
                        return 0
                    case _:
                        print("The effect attribute has an invalid value")
                        return 405
    print("The efects list must have only 2 argument")
    return 402
