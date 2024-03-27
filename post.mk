%:%.cc
	$(CXX) $(CXXFLAGS) $(CPPFLAGS) $(LDFLAGS) -o $@ $^
	@python3 -c 'exec("""import sys,urllib.request\ntry: print(urllib.request.urlopen(urllib.request.Request(url="http://127.0.0.1:17624/eval?"+sys.argv[1], data=sys.argv[2].encode("utf-8"), method="POST")).read().decode(),end="")\nexcept urllib.error.URLError: pass""")' '$(token)' '$(abspath $@)'
