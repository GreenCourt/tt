#!/usr/bin/env python3
import os
import sys
from subprocess import run, Popen, PIPE, TimeoutExpired, CalledProcessError
from threading import Thread
import argparse
from io import StringIO
from datetime import datetime

from common import command, signame, red, cyan, magenta, yellow

def interact(exe1, exe2, timeout, out):
    def io(r, w, label, color):
        for line in r:
            out.write(color(f"[out:{label}] {line.decode()}"))
            try:
                w.writelines([line])
                w.flush()
            except BrokenPipeError:
                pass
        try:
            w.close()
        except BrokenPipeError:
            pass

    def err(r, label):
        for line in r:
            out.write(yellow(f"[err:{label}] {line.decode()}"))

    start_time = datetime.now()
    with Popen(command(exe1), stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc1, \
            Popen(command(exe2), stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc2:

        label1 = exe1.center(max(len(exe1), len(exe2)), " ")
        label2 = exe2.center(max(len(exe1), len(exe2)), " ")

        io1 = Thread(target=io, args=[proc1.stdout, proc2.stdin, label1, magenta])
        io2 = Thread(target=io, args=[proc2.stdout, proc1.stdin, label2, cyan])
        err1 = Thread(target=err, args=[proc1.stderr, label1])
        err2 = Thread(target=err, args=[proc2.stderr, label2])

        err1.start()
        err2.start()

        io1.start()
        io2.start()

        try:
            proc1.wait(timeout=timeout - (datetime.now() - start_time).total_seconds())
            proc2.wait(timeout=timeout - (datetime.now() - start_time).total_seconds())
            tle = False
        except TimeoutExpired:
            tle = True

        proc1.terminate()
        proc2.terminate()
        io1.join()
        err1.join()
        io2.join()
        err2.join()

        proc1.poll()
        proc2.poll()

        ret = False
        if tle:
            out.write(red("TLE") + "\n")
            ret = True
        if proc1.returncode is not None and proc1.returncode != 0:
            out.write(red(f"{exe1}:RE:{signame(proc1.returncode)}") + "\n")
            ret = True
        if proc2.returncode is not None and proc2.returncode != 0:
            out.write(red(f"{exe2}:RE:{signame(proc2.returncode)}") + "\n")
            ret = True

        return ret

def interactive_hack(exe1, exe2, n, timeout):
    if n == 1:
        interact(exe1, exe2, timeout, sys.stdout)
        return

    if not sys.stdout.isatty():
        print("hacking...")

    for i in range(1, n+1):
        if sys.stdout.isatty():
            print("\r\033[2K", i, sep="", end="", flush=True)
        out = StringIO()
        if interact(exe1, exe2, timeout, out):
            if sys.stdout.isatty():
                print()
            print(out.getvalue(), end="")
            return
    if sys.stdout.isatty():
        print()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", metavar="NUMBER_OF_TESTS", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("exe1", type=str)
    parser.add_argument("exe2", type=str)
    args = parser.parse_args()

    try:
        if "MAKELEVEL" not in os.environ:
            try:
                run(["make", "-s", args.exe1, args.exe2], check=True)
            except CalledProcessError as e:
                sys.exit(e.returncode)
        interactive_hack(args.exe1, args.exe2, args.n, args.timeout)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
