#!/usr/bin/env python3
import os
import sys
import json
import signal
import argparse
from subprocess import Popen, TimeoutExpired, PIPE
from multiprocessing import Process
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import urllib.parse
from datetime import datetime
from glob import glob

from common import command, signame, pretty, clear, red, green, yellow, cyan, magenta, diffjudge, load_tolerance

def execute(exe, I, timeout=None):
    r = { "stdout": "", "stderr":"", "returncode":0, "tle":False }
    with Popen(command(exe), stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True) as proc:
        def sigterm_handler(signum, frame):
            if proc:
                proc.kill()
            sys.exit(signum + 128)
        try:
            old = signal.signal(signal.SIGTERM, sigterm_handler)
            r["stdout"], r["stderr"] = proc.communicate(input=I, timeout=timeout)
        except TimeoutExpired:
            proc.kill()
            r["stdout"], r["stderr"] = proc.communicate()
            r["tle"] = True
        finally:
            signal.signal(signal.SIGTERM, old)
        r["returncode"] = proc.returncode
    return r

def evaluate(exe, tests, tolerance=None, timeout=10):
    for n, I, O in tests:
        print(cyan(n + ": "), end="", flush=True)
        r = execute(exe, I, timeout)
        suffix = " stderr" if r["stderr"] else ""

        def print_stderr():
            if r["stderr"]:
                print(yellow("---- stderr ----"))
                print(pretty(r["stderr"]), end="")

        if r["tle"]:
            print(red(f"TLE({timeout}s)"), yellow(suffix), sep="")
            print_stderr()
            continue

        if r["returncode"] != 0:
            print(red("RE:" + signame(r["returncode"])), yellow(suffix), sep="")
            print_stderr()
            continue

        if O is None:
            print(yellow("input-only" + suffix))
            print(magenta("---- actual ----"))
            print(pretty(r["stdout"]), end="")
            print_stderr()
            continue

        ac, float_err = diffjudge(O, r["stdout"], tolerance)

        if float_err is not None:
            suffix += f" err:{float_err:e}"

        if ac:
            print(green("AC"), yellow(suffix), sep="")
        else:
            print(yellow(suffix))
            print(magenta("--- expected ---"))
            print(pretty(O), end="")
            print(magenta("---- actual ----"))
            print(pretty(r["stdout"]), end="")
            print_stderr()

def load(d):
    for i in range(10):
        infile = os.path.join(d, f"in{i}")
        outfile = os.path.join(d, f"out{i}")

        if not os.path.isfile(infile):
            continue

        with open(infile) as f:
            I = f.read()

        O = None
        if os.path.isfile(outfile):
            with open(outfile) as f:
                O = f.read()
        yield f"in{i}", I, O

    if os.path.isdir(os.path.join(d,"in")):
        for i in sorted(os.listdir(os.path.join(d,"in"))):
            infile = os.path.join(d, "in", i)
            outfile = os.path.join(d, "out", i)
            with open(infile) as f:
                I = f.read()
            O = None
            if os.path.isfile(outfile):
                with open(outfile) as f:
                    O = f.read()
            yield f"in/{i}", I, O

class Evaluator:
    tests = []
    proc = None

    @classmethod
    def run(cls, exe):
        Evaluator.terminate()
        clear()
        print("[", datetime.now().strftime("%H:%M:%S"), "] ", exe, sep="")
        if command(exe) is None:
            print("not a executable")
            return
        t = Evaluator.tests if Evaluator.tests else load(os.path.dirname(exe))
        tol = load_tolerance(os.path.dirname(exe))
        Evaluator.proc = Process(target=evaluate, args=(exe, t, tol))
        Evaluator.proc.start()

    @classmethod
    def is_alive(cls):
        return Evaluator.proc is not None and Evaluator.proc.is_alive()

    @classmethod
    def join(cls):
        if Evaluator.is_alive():
            Evaluator.proc.join()
            Evaluator.proc = None

    @classmethod
    def terminate(cls):
        if Evaluator.is_alive():
            Evaluator.proc.terminate()
            Evaluator.proc.join()
        Evaluator.proc = None

def listen(ip, port, token):
    assert(token)

    class PostHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args): pass
        def do_POST(self):
            u = urllib.parse.urlparse(self.path)

            if u.query != token:
                print("invalid token:", u.query)
                self.send_response(400)
                self.end_headers()
                return

            if u.path not in ["/", "/eval"]:
                print("invalid path:", u.path)
                self.send_response(400)
                self.end_headers()
                return

            body = self.rfile.read(int(self.headers['content-length'])).decode('utf-8')

            if u.path == "/eval":
                if not os.path.isabs(body) or not os.path.isfile(body) or \
                    not os.path.commonpath([body, os.getcwd()]) == os.getcwd():
                    print("invalid data:", body)
                    self.send_response(400)
                    self.end_headers()
                    return

                Evaluator.run(os.path.relpath(body))
                self.send_response(200)
                self.end_headers()
                return

            try:
                js = json.loads(body)
            except json.JSONDecodeError:
                print("failed to parse json")
                self.send_response(400)
                self.end_headers()
                return

            if not isinstance(js, dict) \
                    or "url" not in js \
                    or "I" not in js \
                    or "O" not in js \
                    or not isinstance(js["url"], str) \
                    or not isinstance(js["I"], list) \
                    or not isinstance(js["O"], list) \
                    or len(js["I"]) != len(js["O"]) \
                    or not all(isinstance(i, str) for i in js["I"]) \
                    or not all(isinstance(i, str) for i in js["O"]):
                print("invalid json format")
                self.send_response(400)
                self.end_headers()
                return

            clear()
            print("[", datetime.now().strftime("%H:%M:%S"), "] ", js["url"], sep="")

            for i, (I, O) in enumerate(zip(js["I"], js["O"]), start=1):
                print(cyan(f"---- in{i} ----"))
                print(pretty(I), end="")
                print(cyan(f"---- out{i} ---"))
                print(pretty(O), end="")
                print()

            Evaluator.tests = [(f"#{i}", I, O) for i, (I, O) in enumerate(zip(js["I"], js["O"]), start=1)]

            self.send_response(200)
            self.end_headers()

    with HTTPServer((ip,port), PostHandler) as server:
        server.serve_forever()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bind", type=str, default="127.0.0.1")
    parser.add_argument("-p", "--port", type=int, default=17624)
    parser.add_argument("token", type=str)
    args = parser.parse_args()

    if not args.token:
        print("non-empty token required", file=sys.stderr)
        sys.exit(2)

    if not sys.stdout.isatty():
        print("not a tty", file=sys.stderr)
        sys.exit(2)

    def sigterm_handler(signum, frame):
        Evaluator.terminate()
        sys.exit(signum + 128)
    signal.signal(signal.SIGTERM, sigterm_handler)

    try:
        Thread(target=listen, args=(args.bind, args.port, args.token), daemon=True).start()
        while True:
            try:
                input()
                L = list(filter(lambda x: os.path.isfile(x) and os.access(x, os.X_OK), map(lambda x: os.path.splitext(x)[0], glob("**/*.cc", recursive=True)))) \
                    + glob("**/*.py", recursive=True)
                if not L:
                    clear()
                    print("[", datetime.now().strftime("%H:%M:%S"), "] no executable found", sep="")
                    continue
                Evaluator.run(max(L, key=os.path.getmtime))
            except KeyboardInterrupt:
                if Evaluator.is_alive():
                    Evaluator.terminate()
                else:
                    print(" send EOF to exit")
                continue
            except EOFError:
                if not Evaluator.is_alive():
                    break
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
