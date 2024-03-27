l = 1
r = 1000000 + 1;
while r-l > 1:
    m = l + (r-l)//2
    print(m, flush=True)
    res = input()
    assert(res == "<" or res == ">=")
    if res == "<":
        r = m
    else:
        l = m;
print("!", l, flush=True)
