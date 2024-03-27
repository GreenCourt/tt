.PHONY: zipapp
zipapp: serve rh ih

serve: src/serve.py src/common.py
	python3 -m zipapp -c -o $@ -p "/usr/bin/env python3" -m serve:main src

rh: src/random_hack.py src/common.py
	python3 -m zipapp -c -o $@ -p "/usr/bin/env python3" -m random_hack:main src

ih: src/interactive_hack.py src/common.py
	python3 -m zipapp -c -o $@ -p "/usr/bin/env python3" -m interactive_hack:main src
