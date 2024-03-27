#!/usr/bin/env python3
import sys
import urllib.request
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("token", type=str)
args = parser.parse_args()

data = json.dumps({
        "url":"dummy",
        "I": ["1\n", "73\n"],
        "O": ["6.28318530717958623200\n", "458.67252742410977361942\n"]
        }).encode("utf-8")

with urllib.request.urlopen(urllib.request.Request(url="http://127.0.0.1:17624/?"+args.token, data=data, method="POST")) as r:
    print(r.read().decode(), end="")
