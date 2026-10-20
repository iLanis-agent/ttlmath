// TTL Math engine: DNS cache timing arithmetic. How long to wait after lowering a TTL, how many queries caches send, and how long a missing name stays cached. Exact integers.
function _int(t, err, lo, hi) {
  t = typeof t === "string" ? t.trim() : "";
  if (!/^[0-9]{1,7}$/.test(t)) throw new Error(err);
  var v = parseInt(t, 10);
  if (v < lo || v > hi) throw new Error(err);
  return v;
}
function _plural(n, one, many) { return n + " " + (n === 1 ? one : many); }
function _span(n) { // seconds with a days/hours/minutes reading when it is a minute or more
  var s = _plural(n, "second", "seconds");
  if (n < 60) return s;
  var d = Math.floor(n / 86400), h = Math.floor((n % 86400) / 3600), m = Math.floor((n % 3600) / 60), r = n % 60, p = [];
  if (d) p.push(_plural(d, "day", "days"));
  if (h) p.push(_plural(h, "hour", "hours"));
  if (m) p.push(_plural(m, "minute", "minutes"));
  if (r) p.push(_plural(r, "second", "seconds"));
  var t = p.length > 1 ? p.slice(0, -1).join(", ") + " and " + p[p.length - 1] : p[0];
  return s + " (" + t + ")";
}
function _hund(num, den) { // num/den to two decimals, half up, trailing zeros dropped
  var v = Math.floor((2 * num * 100 + den) / (2 * den));
  var f = v % 100, s = String(Math.floor(v / 100));
  if (f === 0) return s;
  return s + "." + (f % 10 === 0 ? String(f / 10) : (f < 10 ? "0" + f : String(f)));
}
var _TERR = "the TTL must be a whole number of seconds from 1 to 2592000";

function waitTruth(oldTtl, newTtl) {
  var o = _int(oldTtl, _TERR, 1, 2592000);
  var n = _int(newTtl, _TERR, 1, 2592000);
  if (n >= o) throw new Error("the lowered TTL must be less than the old TTL");
  return "Lower the TTL from " + _span(o) + " to " + _span(n) + ", then wait at least " + _span(o) + " from that moment before you change the record, because a cache may hold the old answer that long. After the change, a cache can still serve the old answer for at most " + _span(n) + ".";
}
function loadTruth(caches, ttl) {
  var c = _int(caches, "the caches must be a whole number from 1 to 1000000", 1, 1000000);
  var t = _int(ttl, _TERR, 1, 2592000);
  var sec = _hund(c, t), day = Math.floor((2 * c * 86400 + t) / (2 * t));
  var rate = sec === "0" ? "fewer than 0.01 queries" : "at most " + sec + (sec === "1" ? " query" : " queries");
  var perDay = day === 0 ? "fewer than 1 query a day" : "about " + day + (day === 1 ? " query" : " queries") + " a day";
  return _plural(c, "cache", "caches") + " each asking your server at most once every " + _span(t) + (c === 1 ? " sends" : " send") + " it " + rate + " a second, " + perDay + ".";
}
function negTruth(soaTtl, soaMin) {
  var a = _int(soaTtl, "the SOA record TTL must be a whole number of seconds from 0 to 2592000", 0, 2592000);
  var b = _int(soaMin, "the SOA minimum must be a whole number of seconds from 0 to 2592000", 0, 2592000);
  var m = Math.min(a, b);
  if (m === 0) return "The smaller of the two is 0 seconds, so a cache keeps no \"no such name\" answer and a new record can show up at once.";
  return "A cache keeps a \"no such name\" answer for the smaller of two numbers: the SOA record TTL, " + _span(a) + ", and the SOA minimum, " + _span(b) + ". That is " + _span(m) + ", and a record you add for that name may stay unseen that long.";
}
