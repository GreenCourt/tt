#!/usr/bin/env python3
import os
import sys
from subprocess import run, PIPE, DEVNULL, TimeoutExpired, CalledProcessError
import argparse
from difflib import unified_diff

from common import command, signame, pretty, red, cyan, magenta, yellow, diffjudge, load_tolerance

def print_diff(A, B, A_label, B_label):
    a = A.splitlines(keepends=True)
    if A and A[-1] != "\n":
        a[-1] = a[-1] + "(no-eol)"
    b = B.splitlines(keepends=True)
    if B and B[-1] != "\n":
        b[-1] = b[-1] + "(no-eol)"
    sys.stdout.writelines(unified_diff(a, b, fromfile=A_label, tofile=B_label))

def random_hack(generator, exe1, exe2, n, timeout, tolerance):
    def save(I):
        if I is not None:
            with open("failed", "w") as f:
                f.write(I)

    def execute(idx, exe, I):
        if sys.stdout.isatty():
            print("\r\033[2K", idx, " ", exe, " ", sep="", end="", flush=True)
        try:
            return run(command(exe), input=I, stdout=PIPE, stderr=PIPE if I is None else DEVNULL, check=True, timeout=timeout, text=True).stdout
        except TimeoutExpired:
            if sys.stdout.isatty():
                print()
            print(red(f"{exe}:TLE"))
            save(I)
            sys.exit(0)
        except CalledProcessError as e:
            if sys.stdout.isatty():
                print()
            print(red(f"{exe}:RE:{signame(e.returncode)}"))
            if I is None:
                print(yellow("----- stderr -----"))
                print(yellow(pretty(e.stderr)), end="")
            save(I)
            sys.exit(0)

    if not sys.stdout.isatty():
        print("hacking...")

    for i in range(1, n+1):
        I = execute(i, generator, None)
        O1 = execute(i, exe1, I)
        if exe2 is None:
            continue
        O2 = execute(i, exe2, I)
        ac, _ = diffjudge(O2, O1, tolerance)
        if not ac:
            if sys.stdout.isatty():
                print()
            print_diff(O2, O1, exe2, exe1)
            save(I)
            sys.exit(0)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", metavar="NUMBER_OF_TESTS", type=int, default=10000)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("-g", "--generator", type=str, default="g")
    parser.add_argument("-t", "--tolerance", type=float, default=None)
    parser.add_argument("exe1", type=str)
    parser.add_argument("exe2", type=str, nargs="?", default=None)
    args = parser.parse_args()

    try:
        if args.tolerance is None:
            args.tolerance = load_tolerance(os.path.dirname(args.generator))
        if "MAKELEVEL" not in os.environ:
            try:
                run(["make", "-s", args.generator, args.exe1] + ([] if args.exe2 is None else [args.exe2]), check=True)
            except CalledProcessError as e:
                sys.exit(e.returncode)
        random_hack(args.generator, args.exe1, args.exe2, args.n, args.timeout, args.tolerance)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
