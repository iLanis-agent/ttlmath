#!/usr/bin/env python3
# TTL Math oracle - mirrors engine.js independently: the wait is found by replaying every possible fetch moment of a cache and taking the latest expiry, rates use Fractions, spans are built by repeated division, the negative cache is the minimum found by scanning.
import json, re, random
from fractions import Fraction as F
import math

TERR = "the TTL must be a whole number of seconds from 1 to 2592000"

def num(t, err, lo, hi):
    t = t.strip() if isinstance(t, str) else ""
    if not re.fullmatch(r"[0-9]{1,7}", t) or not lo <= int(t) <= hi: raise ValueError(err)
    return int(t)
def pl(n, a, b): return f"{n} {a if n == 1 else b}"
def span(n):
    out = pl(n, "second", "seconds")
    if n < 60: return out
    parts = []; rest = n
    for size, a, b in [(86400, "day", "days"), (3600, "hour", "hours"), (60, "minute", "minutes"), (1, "second", "seconds")]:
        k = 0
        while rest >= size: rest -= size; k += 1
        if k: parts.append(pl(k, a, b))
    text = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]
    return f"{out} ({text})"
def hund(fr):
    v = math.floor(fr * 100 + F(1, 2))
    ip, fp = divmod(v, 100)
    s = f"{fp:02d}".rstrip("0")
    return f"{ip}.{s}" if s else str(ip)
def latest_expiry(ttl):
    # a cache may have fetched at any second in the last ttl seconds before moment 0; its copy expires at fetch + ttl
    return max(f + ttl for f in range(-ttl, 1))

def wait(o, n):
    o = num(o, TERR, 1, 2592000); n = num(n, TERR, 1, 2592000)
    if n >= o: raise ValueError("the lowered TTL must be less than the old TTL")
    w = latest_expiry(o); st = latest_expiry(n)
    return f"Lower the TTL from {span(o)} to {span(n)}, then wait at least {span(w)} from that moment before you change the record, because a cache may hold the old answer that long. After the change, a cache can still serve the old answer for at most {span(st)}."
def load(c, t):
    c = num(c, "the caches must be a whole number from 1 to 1000000", 1, 1000000); t = num(t, TERR, 1, 2592000)
    rate = F(c, t); sec = hund(rate); day = math.floor(rate * 86400 + F(1, 2))
    r = "fewer than 0.01 queries" if sec == "0" else "at most " + sec + (" query" if sec == "1" else " queries")
    d = "fewer than 1 query a day" if day == 0 else "about " + str(day) + (" query" if day == 1 else " queries") + " a day"
    return f"{pl(c,'cache','caches')} each asking your server at most once every {span(t)} {'sends' if c == 1 else 'send'} it {r} a second, {d}."
def neg(a, b):
    a = num(a, "the SOA record TTL must be a whole number of seconds from 0 to 2592000", 0, 2592000)
    b = num(b, "the SOA minimum must be a whole number of seconds from 0 to 2592000", 0, 2592000)
    m = next(x for x in range(0, 2592001) if x == a or x == b)
    if m == 0: return 'The smaller of the two is 0 seconds, so a cache keeps no "no such name" answer and a new record can show up at once.'
    return f'A cache keeps a "no such name" answer for the smaller of two numbers: the SOA record TTL, {span(a)}, and the SOA minimum, {span(b)}. That is {span(m)}, and a record you add for that name may stay unseen that long.'

FNS = {"waitTruth": wait, "loadTruth": load, "negTruth": neg}

def cases():
    c = []
    for o, n in [("86400","300"),("3600","60"),("300","60"),("2","1"),("60","59"),("61","60"),("3601","3600"),("90061","3661"),("86401","1"),("172800","86400"),("604800","3600"),("2592000","1"),("2592000","2591999"),
                 ("300","300"),("300","301"),("1","1"),("1","2"),("0","0"),("0","300"),("300","0"),("2592001","300"),("300","2592001"),("x","300"),("300",""),(" 86400 "," 300 "),("-5","3"),("1.5","1"),("12345678","1")]:
        c.append(("waitTruth", [o, n]))
    for cc, t in [("1000","300"),("1","3"),("1","1"),("1","86400"),("1","2592000"),("1000000","1"),("1000000","2592000"),("1000","2592000"),("3","7"),("2","3"),("5","3"),("7","86400"),("100","60"),("0","300"),("1000001","300"),("1","0"),("1","2592001"),("x","300"),("1000",""),(" 50 "," 20 "),("43200","1"),("1","172800")]:
        c.append(("loadTruth", [cc, t]))
    for a, b in [("3600","900"),("900","3600"),("300","300"),("0","300"),("300","0"),("0","0"),("1","61"),("86400","86400"),("2592000","0"),("2592000","2592000"),("3661","7322"),("2592001","5"),("5","2592001"),("x","5"),("5",""),("-1","5"),(" 60 "," 120 ")]:
        c.append(("negTruth", [a, b]))
    r = random.Random(701)
    for _ in range(25):
        o = r.randint(2, 20000); c.append(("waitTruth", [str(o), str(r.randint(1, o - 1))]))
    for _ in range(40): c.append(("loadTruth", [str(r.randint(1, 5000)), str(r.randint(1, 100000))]))
    for _ in range(25): c.append(("negTruth", [str(r.randint(0, 100000)), str(r.randint(0, 100000))]))
    return c

out = []
for fn, args in cases():
    try: exp = FNS[fn](*args)
    except ValueError as e: exp = "ERR:" + str(e)
    out.append({"fn": fn, "args": args, "expected": exp})
with open("expected.json", "w") as f:
    json.dump(out, f, indent=1); f.write("\n")
print(len(out), "cases written")
