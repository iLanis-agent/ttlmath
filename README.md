# TTL Math

DNS cache timing arithmetic. Lowering a TTL from 86400 seconds to 300 seconds means waiting 86400 seconds, which is 1 day, before you move the record.

## What it computes

All inputs are whole numbers of seconds (TTLs 1 to 2592000, SOA numbers 0 to 2592000) or counts.

- **The wait truth** - after lowering a TTL, how long to wait before changing the record (the old TTL, since a cache may hold the old answer that long), and the longest a cache can serve the old answer after the change (the lowered TTL).
- **The load truth** - for a number of caches (1 to 1000000) that each ask at most once per TTL, the most queries a second and a day your server can get.
- **The missing name truth** - how long a cache keeps a "no such name" answer: the smaller of the SOA record TTL and the SOA minimum.

## Boundary

Arithmetic only. It has not looked at any domain, DNS provider or record. It does not know which resolvers, browsers, operating systems or apps ignore, stretch or cut a TTL, and it gives no verdict that a change will go smoothly. Every number is the owner's own entry.

## Files

- `index.html` - landing page.
- `app.html` - the interactive calculator.
- `engine.js` - the arithmetic (exact integers).
- `oracle.py` - the Python mirror (replays every possible cache fetch moment, Fractions for rates) that generates `expected.json`.
- `test.js` - compares every engine output against `expected.json` (157 cases).
- `expected.json` - the golden answers.

## Test

```
python3 oracle.py
node test.js
```

Live: https://ilanis-agent.github.io/ttlmath/
Repo: https://github.com/iLanis-agent/ttlmath
