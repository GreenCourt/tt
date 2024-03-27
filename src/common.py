import os
import sys
import signal
from math import isnan, isinf

if sys.stdout.isatty():
    def black(x): return "\033[30m" + x + "\033[0m" if x else x
    def red(x): return "\033[31m" + x + "\033[0m" if x else x
    def green(x): return "\033[32m" + x + "\033[0m" if x else x
    def yellow(x): return "\033[33m" + x + "\033[0m" if x else x
    def blue(x): return "\033[34m" + x + "\033[0m" if x else x
    def magenta(x): return "\033[35m" + x + "\033[0m" if x else x
    def cyan(x): return "\033[36m" + x + "\033[0m" if x else x
    def white(x): return "\033[37m" + x + "\033[0m" if x else x
    def clear(): print("\033[2J\033[3J\033[0;0H", end="", flush=True)
else:
    def black(x): return x
    def red(x): return x
    def green(x): return x
    def yellow(x): return x
    def blue(x): return x
    def magenta(x): return x
    def cyan(x): return x
    def white(x): return x
    def clear(): pass

def pretty(text):
    if len(text) == 0:
        return "(empty)\n"
    if len(text) > 10000:
        return "(too long)\n"
    if text and text[-1] != "\n":
        return text + "(no-eol)\n"
    return text

def signame(returncode):
    return signal.Signals(-returncode).name if returncode < 0 else str(returncode)

def command(exe):
    if os.path.isfile(exe):
        if os.access(exe, os.X_OK):
            return [os.path.abspath(exe)]
        if os.path.splitext(exe)[1] == ".py":
            return [sys.executable, os.path.abspath(exe)]
    return None

def equal(expected, actual, tolerance=None):
    assert(tolerance is None or (0 < tolerance < 1))
    if expected == actual:
        return True, None
    try:
        int(expected), int(actual)
        return False, None # if both can be parsed as int
    except ValueError:
        pass
    try:
        exp = float(expected)
        act = float(actual)
        if isnan(exp) or isnan(act) or isinf(exp) or isinf(act):
            return False, None
        abs_err = abs(exp - act)
        rel_err = abs(exp - act) / abs(exp) if abs(exp) > 0 else float("inf")
        err = min(abs_err, rel_err)
        return False if tolerance is None else err < tolerance, err
    except ValueError:
        return False, None

def diffjudge(expected, actual, tolerance=None):
    if expected == actual:
        return True, None
    ac = True
    float_err = None
    try:
        for eline, aline in zip(expected.splitlines(), actual.splitlines(), strict=True):
            for exp, act in zip(eline.split(), aline.split(), strict=True):
                eq, err = equal(exp, act, tolerance)
                ac = ac and eq
                if err is not None:
                    float_err = err if float_err is None else max(float_err, err)
        return ac, float_err
    except ValueError: # raised by zip strict
        return False, None

def load_tolerance(d):
    tolfile = os.path.join(d, "tol")
    if not os.path.isfile(tolfile):
        return None

    with open(tolfile) as f:
        t = f.read()

    try:
        return float(t)
    except ValueError:
        print(red("invalid tolerance"))
        return None
