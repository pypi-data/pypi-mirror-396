import data.colors.colors as cs
import data.efects.efects as es
class PyNewWrite():
    def write(*arg, color: list = False, efects: list = False):
        string = ""
        for i in range(len(arg)):
            string += arg[i] + " "
        if color != False:
            string = cs.main(string , color)
            if efects != False:
                es.main(string , efects)
                return 0
            print(string)
            return 0
        else:
            if efects != False:
                es.main(efects)
                return 0
            print(string)