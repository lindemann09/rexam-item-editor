import argparse
from . import sysinfo

def cli(app_name):
    """returns dict with selected command line option"""

    parser = argparse.ArgumentParser(
        description=app_name,
        epilog="(c) O. Lindemann, 2021")

    parser.add_argument("-r", "--reset",
                        action="store_true",
                        help="reset app and remove settings file",
                        default=False)

    parser.add_argument("-i", "--info",
                        action="store_true",
                        help="display system info",
                        default=False)

    parser.add_argument("-m", "--monolingual",
                        action="store_true",
                        help="switch to monolingual mode (default is "
                             "bilingual)",
                        default=False)

    parser.add_argument("-e", "--exam_compiler",
                        action="store_true",
                        help="run exam compiler",
                        default=False)

    parser.add_argument("-c", "--r_code", nargs='?', metavar="JSON-FILE", type=str,
                        help="convert exam-file to r code",
                        default="False")


    opt = vars(parser.parse_args())

    if opt["info"]:
        print(app_name)
        print("\n".join(sysinfo.info()))
        exit()
    if opt["r_code"] is None:
        parser.print_help()
        print("")
        print("Please specify exam file.")
        exit()

    return opt
