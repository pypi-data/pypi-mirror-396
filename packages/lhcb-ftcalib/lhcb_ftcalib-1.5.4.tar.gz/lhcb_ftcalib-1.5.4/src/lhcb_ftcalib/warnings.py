import atexit
from typing import List

print_warning_summary = True

class FTCWarning:
    def __init__(self, warntype: str, msg: str):
        self.warntype = warntype
        self.msg = msg
        self.multiplicity = 1

    def __str__(self) -> str:
        if self.multiplicity > 1:
            return f"\033[33m\033[1m - (x{self.multiplicity}) [{self.warntype}]\033[0m {self.msg}"  # ]]]
        return f"\033[33m\033[1m - [{self.warntype}]\033[0m {self.msg}"  # ]]]

    def __eq__(self, other) -> bool:
        return self.warntype == other.warntype and self.msg == other.msg

collected_ftcalib_warnings: List[FTCWarning] = []


def ftcalib_warning(warningType: str, message: str, printNow: bool = True):
    """Print warning and save it for later summary."""

    thewarning = FTCWarning(warningType, message)

    if thewarning not in collected_ftcalib_warnings:
        collected_ftcalib_warnings.append(FTCWarning(warningType, message))
    else:
        idx = collected_ftcalib_warnings.index(thewarning)
        collected_ftcalib_warnings[idx].multiplicity += 1

    if printNow:
        print(collected_ftcalib_warnings[-1])

def print_all_warnings_again():
    """Print all collected FTCalib warnings."""

    if collected_ftcalib_warnings and print_warning_summary:
        print("\n\033[33m\033[1m ▲ ▲ ▲ Warning report ▲ ▲ ▲\033[0m")  # ]]]
        for warning in collected_ftcalib_warnings:
            print(str(warning))

atexit.register(print_all_warnings_again)
