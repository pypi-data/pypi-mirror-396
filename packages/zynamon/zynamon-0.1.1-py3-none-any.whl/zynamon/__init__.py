""" Generalized & powerful time-series class and related functions """

__author__ = 'Dr. Marcus Zeller (dsp4444@gmail.com)'
__version__ = '0.1.1'
__all__ = []

example = [
    "from zynamon.zeit import TimeSeries",
    "ts = TimeSeries('MyNew1')",
    "ts.tags_register({'location': 'Erlangen', 'reason': 'Just-a-test'})",
    "apples = [0.1, 1.1, 2.95, 2.6, 3.4, 4, 3.2, 5.1777]",
    "pears  = [10, 20, 30, 40, 50, 60, 70, 80]",
    "ts.samples_add(zip(apples, pears))",
    "ts.print()",
    "ts.time.stat",
    "ts.time_causalise()",
    "ts.time_align(res=0.5, shift='bwd', recon='avg')",
    "ts.print(25)",
    "ts.time.stat"
]

def demo():
    print("This is a demo for the 'zynamon' package.")
    print("")
    print("Usage example:")
    for line in example:
        print(" "*4+line)
    print("")
    chk = input('Do you want to run this now? (y/N)')
    if (chk.lower() == 'y'):
        for line in example:
            exec(line)
    print("Have phun! :)")
    return
