#!/usr/bin/env python3
"""i4f - deterministic toolkit for the invest-4-future markdown brain.

Stdlib only, no install step. Runs on any Python 3.8+. The point of this
tool is to give a local agent (Hermes, Open Interpreter, Goose, Claude
Code, ...) operations it can run *deterministically* instead of
hand-editing index files and guessing IDs.

    python3 tools/i4f.py validate     # check every artifact's front-matter
    python3 tools/i4f.py index        # rebuild hypotheses/ + recommendations/ indices
    python3 tools/i4f.py status       # snapshot of live state (--json for agents)
    python3 tools/i4f.py new ...      # scaffold a new episode/hypothesis/recommendation
    python3 tools/i4f.py review       # list hypotheses/positions due for review
    python3 tools/i4f.py scorecard    # rebuild the calibration track record

Indices and IDs become a pure function of the artifact files. An agent
never invents an index row or a duplicate ID again. review + scorecard
close the loop: surface what is due, then score what has closed so the
playbook can be corrected on evidence.
"""
import argparse
import calendar
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXCHANGES = {"NASDAQ", "NYSE", "OSL", "AMS", "STO", "LON", "EPA", "FRA"}
HYP_VERDICTS = {"non-consensus", "priced-in", "hype", "too-early"}
HYP_STATUS = {"ACTIVE", "CONFIRMED", "FALSIFIED", "EXPIRED", "REJECTED"}
REC_STATUS = {"NEW", "WATCHING", "BOUGHT", "TRIMMED", "EXITED", "REJECTED"}

EPISODE_ID_RE = re.compile(r"^MS-\d{4}-\d{2}-\d{2}$")
HYP_ID_RE = re.compile(r"^MS-\d{4}-\d{2}-\d{2}-H\d+$")


# --------------------------------------------------------------------------
# front-matter parsing (minimal YAML subset - flat keys, inline lists)
# --------------------------------------------------------------------------
def _strip_comment(val):
    if val.startswith("#"):
        return ""
    if val.startswith('"'):
        m = re.match(r'"[^"]*"', val)
        return m.group(0) if m else val
    if val.startswith("["):
        idx = val.find("]")
        return val[: idx + 1] if idx != -1 else val
    if " #" in val:
        return val.split(" #", 1)[0].rstrip()
    return val


def _parse_value(val):
    if val == "":
        return ""
    if val.startswith('"') and val.endswith('"'):
        return val[1:-1]
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner:
            return []
        return [x.strip().strip('"') for x in inner.split(",") if x.strip()]
    low = val.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        pass
    return val


def parse_frontmatter(text):
    """Return (frontmatter_dict, body_str)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text
    fm = {}
    for line in lines[1:end]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in line:
            continue
        key, _, raw = line.partition(":")
        fm[key.strip()] = _parse_value(_strip_comment(raw.strip()))
    return fm, "\n".join(lines[end + 1 :])


def load_dir(subdir):
    """Load every artifact in subdir, skipping _index/_template files."""
    out = []
    for path in sorted((ROOT / subdir).glob("*.md")):
        if path.name.startswith("_"):
            continue
        fm, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        out.append((path, fm, body))
    return out


def section(body, title_prefix):
    """Return the lines of the first '## <title_prefix>...' section."""
    out, capturing = [], False
    for ln in body.split("\n"):
        if ln.startswith("## "):
            capturing = ln[3:].strip().lower().startswith(title_prefix)
            continue
        if capturing:
            out.append(ln)
    return "\n".join(out).strip()


def add_months(iso_date, months):
    """Return the date `months` after an ISO date string, clamping the day."""
    y, m, d = (int(x) for x in iso_date.split("-"))
    ny, nm = divmod(y * 12 + (m - 1) + months, 12)
    nm += 1
    return date(ny, nm, min(d, calendar.monthrange(ny, nm)[1]))


def _age_days(value, today):
    """Days between an ISO date string and today, or None if unparseable."""
    if not value:
        return None
    try:
        return (today - date.fromisoformat(str(value))).days
    except ValueError:
        return None


# --------------------------------------------------------------------------
# validate
# --------------------------------------------------------------------------
def _require(fm, keys, ctx, errors):
    for k in keys:
        if k not in fm or fm[k] == "" or fm[k] is None:
            errors.append(f"{ctx}: missing required field '{k}'")


def collect(errors, warnings):
    episodes = load_dir("episodes")
    hypotheses = load_dir("hypotheses")
    recommendations = load_dir("recommendations")

    episode_ids = {fm.get("id") for _, fm, _ in episodes}
    hyp_ids = {fm.get("id") for _, fm, _ in hypotheses}

    for path, fm, _ in episodes:
        ctx = f"episodes/{path.name}"
        _require(fm, ["id", "title", "date", "processed"], ctx, errors)
        eid = str(fm.get("id", ""))
        if eid and not EPISODE_ID_RE.match(eid):
            errors.append(f"{ctx}: id '{eid}' is not MS-YYYY-MM-DD")
        if eid and eid != path.stem:
            errors.append(f"{ctx}: id '{eid}' does not match filename")

    for path, fm, _ in hypotheses:
        ctx = f"hypotheses/{path.name}"
        _require(
            fm,
            ["id", "episode", "theme", "verdict", "status", "conviction"],
            ctx,
            errors,
        )
        hid = str(fm.get("id", ""))
        if hid and not HYP_ID_RE.match(hid):
            errors.append(f"{ctx}: id '{hid}' is not MS-YYYY-MM-DD-H{{n}}")
        if hid and hid != path.stem:
            errors.append(f"{ctx}: id '{hid}' does not match filename")
        if fm.get("episode") and fm["episode"] not in episode_ids:
            errors.append(f"{ctx}: episode '{fm['episode']}' has no file in episodes/")
        if fm.get("verdict") and fm["verdict"] not in HYP_VERDICTS:
            errors.append(f"{ctx}: verdict '{fm['verdict']}' not in {sorted(HYP_VERDICTS)}")
        if fm.get("status") and fm["status"] not in HYP_STATUS:
            errors.append(f"{ctx}: status '{fm['status']}' not in {sorted(HYP_STATUS)}")
        conv = fm.get("conviction")
        if isinstance(conv, int) and not 1 <= conv <= 5:
            errors.append(f"{ctx}: conviction {conv} outside 1-5")
        if fm.get("status") == "REJECTED" and not section(_, "why rejected"):
            warnings.append(f"{ctx}: status REJECTED but no '## Why rejected' section")

    for path, fm, _ in recommendations:
        ctx = f"recommendations/{path.name}"
        _require(
            fm,
            ["ticker", "exchange", "company", "hypothesis_id", "status", "conviction"],
            ctx,
            errors,
        )
        if fm.get("ticker") and fm["ticker"] != path.stem:
            errors.append(f"{ctx}: ticker '{fm['ticker']}' does not match filename")
        if fm.get("exchange") and fm["exchange"] not in EXCHANGES:
            errors.append(f"{ctx}: exchange '{fm['exchange']}' not in {sorted(EXCHANGES)}")
        if fm.get("status") and fm["status"] not in REC_STATUS:
            errors.append(f"{ctx}: status '{fm['status']}' not in {sorted(REC_STATUS)}")
        if fm.get("hypothesis_id") and fm["hypothesis_id"] not in hyp_ids:
            errors.append(
                f"{ctx}: hypothesis_id '{fm['hypothesis_id']}' has no file in hypotheses/"
            )
        up, down, asym = fm.get("upside_pct"), fm.get("downside_pct"), fm.get("asymmetry")
        if all(isinstance(x, (int, float)) for x in (up, down, asym)) and down:
            expected = round(abs(up / down), 2)
            if asym and abs(expected - asym) > 0.15:
                warnings.append(
                    f"{ctx}: asymmetry {asym} != upside/|downside| ({expected})"
                )

    return episodes, hypotheses, recommendations


def cmd_validate(args):
    errors, warnings = [], []
    collect(errors, warnings)

    stale = [name for name, (_, changed) in _build_indices().items() if changed]
    if stale:
        warnings.append(
            "indices stale (" + ", ".join(stale) + ") - run: python3 tools/i4f.py index"
        )
    if _build_scorecard()[1]:
        warnings.append("brain/scorecard.md stale - run: python3 tools/i4f.py scorecard")

    for w in warnings:
        print(f"warn:  {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"ok - all artifacts valid ({len(warnings)} warning(s))")
    return 0


# --------------------------------------------------------------------------
# index
# --------------------------------------------------------------------------
def _reject_reason(body, fm):
    for ln in section(body, "why rejected").split("\n"):
        ln = re.sub(r"\*+", "", ln.strip().lstrip("-*").strip())
        if not ln:
            continue
        first = ln.split(". ", 1)[0].rstrip(".")
        if len(first) <= 110:
            return first + "."
        cut = first[:100].rsplit(" ", 1)[0]
        return cut + " …"
    return fm.get("verdict", "")


def _hyp_index_text(hypotheses):
    def conv(fm):
        return fm.get("conviction") if isinstance(fm.get("conviction"), int) else 0

    active = sorted(
        (h for h in hypotheses if h[1].get("status") == "ACTIVE"),
        key=lambda h: (-conv(h[1]), h[1].get("id", "")),
    )
    rejected = [h for h in hypotheses if h[1].get("status") == "REJECTED"]
    closed = [
        h for h in hypotheses if h[1].get("status") in ("CONFIRMED", "FALSIFIED", "EXPIRED")
    ]

    out = [
        "# Hypotheses index",
        "",
        "Rebuilt by `tools/i4f.py index`. Source of truth for \"what is live.\"",
        "",
        "## Active",
        "",
        "| ID | Theme | Horizon | Conviction | Verdict | Tickers |",
        "|---|---|---|---|---|---|",
    ]
    for path, fm, _ in active:
        tickers = ", ".join(fm.get("related_tickers") or [])
        out.append(
            f"| [{fm['id']}]({path.name}) | {fm.get('theme', '')} | "
            f"{fm.get('horizon_months', '')}m | {fm.get('conviction', '')} | "
            f"{fm.get('verdict', '')} | {tickers} |"
        )
    out += ["", "## Rejected (kept for reference)", "", "| ID | Theme | Reason |", "|---|---|---|"]
    for path, fm, body in rejected:
        out.append(
            f"| [{fm['id']}]({path.name}) | {fm.get('theme', '')} | {_reject_reason(body, fm)} |"
        )
    out += ["", "## Confirmed / Falsified / Expired", ""]
    if closed:
        out += ["| ID | Theme | Status |", "|---|---|---|"]
        for path, fm, _ in closed:
            out.append(f"| [{fm['id']}]({path.name}) | {fm.get('theme', '')} | {fm['status']} |")
    else:
        out.append("(none yet)")
    return "\n".join(out) + "\n"


def _num(v):
    if isinstance(v, float) and v.is_integer():
        return str(v)
    return str(v)


def _rec_index_text(recommendations):
    def conv(fm):
        return fm.get("conviction") if isinstance(fm.get("conviction"), int) else 0

    def hyp_link(fm):
        hid = fm.get("hypothesis_id", "")
        return f"[{hid}](../hypotheses/{hid}.md)" if hid else ""

    def by_conv(items):
        return sorted(items, key=lambda r: (-conv(r[1]), r[1].get("ticker", "")))

    new = by_conv(r for r in recommendations if r[1].get("status") in ("NEW", "WATCHING"))
    bought = by_conv(r for r in recommendations if r[1].get("status") in ("BOUGHT", "TRIMMED"))
    closed = by_conv(r for r in recommendations if r[1].get("status") in ("REJECTED", "EXITED"))

    out = [
        "# Recommendations index",
        "",
        "Rebuilt by `tools/i4f.py index`.",
        "",
        "## NEW / WATCHING (not yet acted on)",
        "",
        "| Ticker | Exchange | Hypothesis | Conviction | Asymmetry | Entry zone | Size | ASK |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for path, fm, _ in new:
        ask = "✅" if fm.get("ask_eligible") else "❌"
        out.append(
            f"| [{fm['ticker']}]({path.name}) | {fm.get('exchange', '')} | {hyp_link(fm)} | "
            f"{fm.get('conviction', '')} | {_num(fm.get('asymmetry', ''))}x | "
            f"{fm.get('entry_zone', '')} | {_num(fm.get('position_size_pct', ''))} % | {ask} |"
        )
    out += [
        "",
        "## BOUGHT / TRIMMED",
        "",
        "| Ticker | Exchange | Hypothesis | Status | Asymmetry |",
        "|---|---|---|---|---|",
    ]
    for path, fm, _ in bought:
        out.append(
            f"| [{fm['ticker']}]({path.name}) | {fm.get('exchange', '')} | {hyp_link(fm)} | "
            f"{fm.get('status', '')} | {_num(fm.get('asymmetry', ''))}x |"
        )
    out += ["", "## REJECTED / EXITED", ""]
    if closed:
        out += ["| Ticker | Exchange | Hypothesis | Status |", "|---|---|---|---|"]
        for path, fm, _ in closed:
            out.append(
                f"| [{fm['ticker']}]({path.name}) | {fm.get('exchange', '')} | "
                f"{hyp_link(fm)} | {fm.get('status', '')} |"
            )
    else:
        out.append("(none yet)")
    return "\n".join(out) + "\n"


def _build_indices():
    """Return {relpath: (new_text, changed_bool)}."""
    hypotheses = load_dir("hypotheses")
    recommendations = load_dir("recommendations")
    result = {}
    for relpath, text in (
        ("hypotheses/_index.md", _hyp_index_text(hypotheses)),
        ("recommendations/_index.md", _rec_index_text(recommendations)),
    ):
        current = (ROOT / relpath).read_text(encoding="utf-8") if (ROOT / relpath).exists() else ""
        result[relpath] = (text, text != current)
    return result


def cmd_index(args):
    indices = _build_indices()
    changed = {k: v for k, v in indices.items() if v[1]}
    if args.check:
        for name in indices:
            print(f"{'STALE' if indices[name][1] else 'ok'}  {name}")
        return 1 if changed else 0
    for relpath, (text, is_changed) in indices.items():
        if is_changed:
            (ROOT / relpath).write_text(text, encoding="utf-8")
            print(f"rewrote {relpath}")
        else:
            print(f"ok      {relpath} (unchanged)")
    return 0


# --------------------------------------------------------------------------
# status
# --------------------------------------------------------------------------
def cmd_status(args):
    episodes, hypotheses, recommendations = collect([], [])

    def counts(items, statuses):
        c = {s: 0 for s in statuses}
        for _, fm, _ in items:
            if fm.get("status") in c:
                c[fm["status"]] += 1
        return c

    active = sorted(
        (
            {
                "id": fm.get("id"),
                "theme": fm.get("theme"),
                "conviction": fm.get("conviction"),
                "verdict": fm.get("verdict"),
            }
            for _, fm, _ in hypotheses
            if fm.get("status") == "ACTIVE"
        ),
        key=lambda h: -(h["conviction"] if isinstance(h["conviction"], int) else 0),
    )
    watchlist = [
        {
            "ticker": fm.get("ticker"),
            "asymmetry": fm.get("asymmetry"),
            "entry_zone": fm.get("entry_zone"),
            "ask_eligible": fm.get("ask_eligible"),
        }
        for _, fm, _ in recommendations
        if fm.get("status") in ("NEW", "WATCHING")
    ]
    data = {
        "episodes": len(episodes),
        "hypotheses": counts(hypotheses, HYP_STATUS),
        "recommendations": counts(recommendations, REC_STATUS),
        "active_hypotheses": active,
        "watchlist": watchlist,
    }

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    print(f"episodes:        {data['episodes']}")
    print("hypotheses:      " + ", ".join(f"{k} {v}" for k, v in data["hypotheses"].items() if v))
    print(
        "recommendations: "
        + ", ".join(f"{k} {v}" for k, v in data["recommendations"].items() if v)
    )
    print("\nactive hypotheses (conviction desc):")
    for h in active:
        print(f"  [{h['conviction']}] {h['id']:<22} {h['theme']}  ({h['verdict']})")
    print("\nwatchlist (NEW / WATCHING):")
    for w in watchlist:
        flag = "ASK" if w["ask_eligible"] else "ord"
        print(f"  {w['ticker']:<6} asym {w['asymmetry']}x  {w['entry_zone']}  [{flag}]")
    return 0


# --------------------------------------------------------------------------
# new
# --------------------------------------------------------------------------
def _render_template(tpl_relpath, updates, body_subs=None):
    text = (ROOT / tpl_relpath).read_text(encoding="utf-8")
    lines = text.split("\n")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end:
        for i in range(1, end):
            key = lines[i].split(":", 1)[0].strip()
            if key in updates:
                lines[i] = f"{key}: {updates[key]}"
    text = "\n".join(lines)
    for old, new in (body_subs or {}).items():
        text = text.replace(old, new)
    return text


def _write_new(relpath, text):
    path = ROOT / relpath
    if path.exists():
        print(f"ERROR: {relpath} already exists", file=sys.stderr)
        return 1
    path.write_text(text, encoding="utf-8")
    print(f"created {relpath}")
    return 0


def cmd_new(args):
    today = date.today().isoformat()
    if args.kind == "episode":
        if not EPISODE_ID_RE.match(f"MS-{args.date}"):
            print("ERROR: --date must be YYYY-MM-DD", file=sys.stderr)
            return 1
        eid = f"MS-{args.date}"
        text = _render_template(
            "episodes/_template.md",
            {"id": eid, "title": f'"{args.title}"', "date": args.date, "processed": "false"},
            {"# {title}": f"# {args.title}"},
        )
        return _write_new(f"episodes/{eid}.md", text)

    if args.kind == "hypothesis":
        if not EPISODE_ID_RE.match(args.episode):
            print("ERROR: --episode must be MS-YYYY-MM-DD", file=sys.stderr)
            return 1
        n = 1 + max(
            (
                int(re.match(rf"^{re.escape(args.episode)}-H(\d+)$", str(fm.get("id", ""))).group(1))
                for _, fm, _ in load_dir("hypotheses")
                if re.match(rf"^{re.escape(args.episode)}-H\d+$", str(fm.get("id", "")))
            ),
            default=0,
        )
        hid = f"{args.episode}-H{n}"
        text = _render_template(
            "hypotheses/_template.md",
            {
                "id": hid,
                "episode": args.episode,
                "created": today,
                "updated": today,
                **({"theme": f'"{args.theme}"'} if args.theme else {}),
            },
        )
        return _write_new(f"hypotheses/{hid}.md", text)

    if args.kind == "recommendation":
        if args.ticker != args.ticker.upper():
            print("ERROR: --ticker must be uppercase", file=sys.stderr)
            return 1
        text = _render_template(
            "recommendations/_template.md",
            {
                "ticker": args.ticker,
                "exchange": args.exchange,
                "company": f'"{args.company}"',
                "hypothesis_id": args.hypothesis,
                "created": today,
                "updated": today,
            },
        )
        return _write_new(f"recommendations/{args.ticker}.md", text)
    return 1


# --------------------------------------------------------------------------
# review + scorecard - the self-improvement loop
# --------------------------------------------------------------------------
def cmd_review(args):
    today = date.today()
    hyp_due, rec_due = [], []

    for _, fm, _ in load_dir("hypotheses"):
        if fm.get("status") != "ACTIVE":
            continue
        reasons = []
        created, horizon = fm.get("created"), fm.get("horizon_months")
        if created and isinstance(horizon, int):
            try:
                elapsed = add_months(str(created), horizon)
                if elapsed <= today:
                    reasons.append(f"horizon elapsed {elapsed.isoformat()}")
            except (ValueError, TypeError):
                pass
        age = _age_days(fm.get("reviewed") or fm.get("updated"), today)
        if age is not None and age > args.stale_days:
            reasons.append(f"not reviewed in {age}d")
        if reasons:
            hyp_due.append({"id": fm.get("id"), "theme": fm.get("theme"), "reasons": reasons})

    for _, fm, _ in load_dir("recommendations"):
        if fm.get("status") not in ("BOUGHT", "TRIMMED"):
            continue
        age = _age_days(fm.get("reviewed") or fm.get("updated"), today)
        if age is not None and age > args.stale_days:
            rec_due.append(
                {"ticker": fm.get("ticker"), "reasons": [f"position not reviewed in {age}d"]}
            )

    if args.json:
        print(json.dumps({"hypotheses": hyp_due, "recommendations": rec_due}, indent=2,
                         ensure_ascii=False))
        return 0

    if not hyp_due and not rec_due:
        print("nothing due for review")
        return 0
    if hyp_due:
        print("hypotheses due for review:")
        for h in hyp_due:
            print(f"  {h['id']:<22} {h['theme']}")
            for r in h["reasons"]:
                print(f"      - {r}")
    if rec_due:
        if hyp_due:
            print()
        print("positions due for review:")
        for r in rec_due:
            print(f"  {r['ticker']:<6} {r['reasons'][0]}")
    return 0


def _scorecard_text(hypotheses, recommendations):
    closed = [h for h in hypotheses if h[1].get("status") in ("CONFIRMED", "FALSIFIED", "EXPIRED")]
    active = [h for h in hypotheses if h[1].get("status") == "ACTIVE"]
    realized = [r for r in recommendations if isinstance(r[1].get("realized_pct"), (int, float))]

    out = [
        "# Scorecard - calibration track record",
        "",
        "Rebuilt by `tools/i4f.py scorecard`. This is the self-improvement",
        "layer's memory: it measures whether the process's own calls were",
        "right, so `playbook.md` gets corrected on evidence, not vibes.",
        "",
        f"`{len(closed)}` hypotheses closed - `{len(realized)}` recommendations realized.",
        "",
        "## Closed hypotheses",
        "",
    ]
    if closed:
        out += ["| ID | Theme | Verdict | Conviction | Outcome |", "|---|---|---|---|---|"]
        for path, fm, _ in sorted(closed, key=lambda h: h[1].get("id", "")):
            out.append(
                f"| [{fm['id']}](../hypotheses/{path.name}) | {fm.get('theme', '')} | "
                f"{fm.get('verdict', '')} | {fm.get('conviction', '')} | {fm.get('status', '')} |"
            )
    else:
        out.append("(none yet)")

    out += ["", "## Verdict accuracy", ""]
    nonconsensus = [h for h in closed if h[1].get("verdict") == "non-consensus"]
    if nonconsensus:
        hit = sum(1 for h in nonconsensus if h[1].get("status") == "CONFIRMED")
        out.append(
            f"non-consensus hypotheses confirmed: {hit} / {len(nonconsensus)} "
            f"({round(100 * hit / len(nonconsensus))} %)"
        )
    else:
        out.append("(none yet - needs closed non-consensus hypotheses)")

    out += [
        "",
        "## Conviction calibration",
        "",
        "Do high-conviction calls actually confirm more often? If not, the",
        "conviction tiers in `mandate.md` are miscalibrated.",
        "",
    ]
    if closed:
        out += ["| Conviction | Closed | Confirmed | Confirm rate |", "|---|---|---|---|"]
        for tier in (5, 4, 3, 2, 1):
            grp = [h for h in closed if h[1].get("conviction") == tier]
            if not grp:
                continue
            hit = sum(1 for h in grp if h[1].get("status") == "CONFIRMED")
            out.append(f"| {tier} | {len(grp)} | {hit} | {round(100 * hit / len(grp))} % |")
    else:
        out.append("(none yet)")

    out += [
        "",
        "## Recommendation calibration (estimated vs realized)",
        "",
        "Was the asymmetry estimate honest in hindsight?",
        "",
    ]
    if realized:
        out += [
            "| Ticker | Est. upside | Est. downside | Realized | In band |",
            "|---|---|---|---|---|",
        ]
        in_band = 0
        for path, fm, _ in sorted(realized, key=lambda r: r[1].get("ticker", "")):
            up, dn, rz = fm.get("upside_pct"), fm.get("downside_pct"), fm.get("realized_pct")
            band = isinstance(up, (int, float)) and isinstance(dn, (int, float)) and dn <= rz <= up
            in_band += 1 if band else 0
            out.append(
                f"| [{fm['ticker']}](../recommendations/{path.name}) | {up} % | {dn} % | "
                f"{rz} % | {'yes' if band else 'no'} |"
            )
        out += ["", f"Realized return inside the estimated band: {in_band} / {len(realized)}."]
    else:
        out.append("(none yet - needs recommendations with `realized_pct` set)")

    out += [
        "",
        "## Open items",
        "",
        f"`{len(active)}` active hypotheses awaiting outcome. "
        "Run `python3 tools/i4f.py review` for what is due.",
    ]
    return "\n".join(out) + "\n"


def _build_scorecard():
    """Return (scorecard_text, changed_bool)."""
    text = _scorecard_text(load_dir("hypotheses"), load_dir("recommendations"))
    path = ROOT / "brain" / "scorecard.md"
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    return text, text != current


def cmd_scorecard(args):
    text, changed = _build_scorecard()
    if args.check:
        print(f"{'STALE' if changed else 'ok'}  brain/scorecard.md")
        return 1 if changed else 0
    if changed:
        (ROOT / "brain" / "scorecard.md").write_text(text, encoding="utf-8")
        print("rewrote brain/scorecard.md")
    else:
        print("ok      brain/scorecard.md (unchanged)")
    return 0


# --------------------------------------------------------------------------
def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="i4f", description="Deterministic toolkit for the invest-4-future brain."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("validate", help="check every artifact's front-matter").set_defaults(
        func=cmd_validate
    )

    p_index = sub.add_parser("index", help="rebuild the _index.md files")
    p_index.add_argument(
        "--check", action="store_true", help="report staleness without writing (exit 1 if stale)"
    )
    p_index.set_defaults(func=cmd_index)

    p_status = sub.add_parser("status", help="snapshot of live state")
    p_status.add_argument("--json", action="store_true", help="machine-readable output")
    p_status.set_defaults(func=cmd_status)

    p_new = sub.add_parser("new", help="scaffold a new artifact from its template")
    new_sub = p_new.add_subparsers(dest="kind", required=True)
    p_ep = new_sub.add_parser("episode")
    p_ep.add_argument("--date", required=True, help="YYYY-MM-DD")
    p_ep.add_argument("--title", required=True)
    p_hy = new_sub.add_parser("hypothesis")
    p_hy.add_argument("--episode", required=True, help="MS-YYYY-MM-DD")
    p_hy.add_argument("--theme", default="")
    p_rec = new_sub.add_parser("recommendation")
    p_rec.add_argument("--ticker", required=True)
    p_rec.add_argument("--exchange", required=True, choices=sorted(EXCHANGES))
    p_rec.add_argument("--company", required=True)
    p_rec.add_argument("--hypothesis", required=True, help="hypothesis id")
    p_new.set_defaults(func=cmd_new)

    p_review = sub.add_parser("review", help="list hypotheses/positions due for review")
    p_review.add_argument("--json", action="store_true", help="machine-readable output")
    p_review.add_argument(
        "--stale-days", type=int, default=90, help="flag artifacts not reviewed in N days"
    )
    p_review.set_defaults(func=cmd_review)

    p_score = sub.add_parser("scorecard", help="rebuild brain/scorecard.md from closed artifacts")
    p_score.add_argument("--check", action="store_true", help="report staleness without writing")
    p_score.set_defaults(func=cmd_scorecard)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
