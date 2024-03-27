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
        "I": ["3200\npink\n", "3199\npink\n", "4049\nred\n"],
        "O": ["pink\n", "red\n", "red\n"]
        }).encode("utf-8")

with urllib.request.urlopen(urllib.request.Request(url="http://127.0.0.1:17624/?"+args.token, data=data, method="POST")) as r:
    print(r.read().decode(), end="")
