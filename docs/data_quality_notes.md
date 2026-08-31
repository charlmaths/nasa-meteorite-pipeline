# Data Quality Notes — `pipeline/data_quality.py`

Working notes for the data quality stage. Captures **what each data quality check does**, the
**approaches I tried** to get there, and the **refactors** I still want to make so
the script reads cleaner.

This is a learning journal as much as a spec — the "trial" sections are kept on
purpose so I can see why the current version looks the way it does.

---

## 1. Purpose

The ingest stage (`pipeline/ingest.py`) lands raw JSON from NASA's meteorite
landings API straight to disk with no validation. This stage reads that file back
and answers one question per check: **is this field trustworthy enough to load
into BigQuery?**.

Records that fail should eventually be routed to a quarantine file rather than
dropped silently, so nothing disappears without a trace. Trying to replicate a real production architecture, the checks are read-only and don't mutate the payload. Maybe I'll add like a warning or alert.

---

## 2. Data shape

Sample record from `data/nasa-json-api/meteor_data.json`:

```json
{
  "name": "Aachen",
  "id": "1",
  "nametype": "Valid",
  "recclass": "L5",
  "mass": "21",
  "fall": "Fell",
  "year": "1880-01-01T00:00:00.000",
  "reclat": "50.775000",
  "reclong": "6.083330",
  "geolocation": { "latitude": "50.775", "longitude": "6.08333" }
}
```

Things worth noting:

- Every value is a **string**, including `id`, `mass`, `reclat`, `reclong`.
- `year` is an ISO timestamp string; only the first 4 chars are the year.
- Some records are missing keys entirely (`year`, `mass`, `geolocation`).
- Extra Socrata system keys show up on some records
  (`:@computed_region_nnqa_25f4`, `:@computed_region_cbhk_fwbd`) — ignore these.
- `~1000` records in the test extract (`?$limit=1000`).

---

## 3. Design approach

- One function per check. Each takes the full `payload` (list of dicts) and
  returns the records / names that failed.
- Checks are **read-only** — they report, they don't mutate or filter. Filtering
  and quarantine routing happen in one place after all checks run.
- Iterate with `for record in payload:` rather than `while i < len(payload)` —
  no index bookkeeping, no `payload[i]["..."]` noise (see trials below).
- Guard missing keys with `record.get("key")` or `"key" in record` before
  touching the value.

Target end state:

```
main()
  └─ load file
  └─ run each check → collect failures
  └─ split payload into clean / quarantine
  └─ write clean + quarantine files, print a summary
```

---

## 4. Checks

### 4.1 `null_check(payload)` — status: working, needs cleanup

**Goal:** flag records where `id` is missing / null / blank.

**Current logic:**

```python
for record in payload:
    if record["id"] is None or record["id"].strip() == "":
        id_null_list.append(record["name"])
```

**Trials:**

| Approach                                      | What happened                                                                                       | Verdict                     |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------- | --------------------------- |
| `while i < len(payload)` + `payload[i]["id"]` | Worked, but every line carried an `[i]` and I had to remember `i += 1`. Hard to read.               | Dropped                     |
| `for record in payload`                       | Same logic, no index. Reads like a sentence.                                                        | **Kept**                    |
| `record["id"]` direct access                  | Throws `KeyError` if the key is absent (vs. present-but-null).                                      | Needs fixing → use `.get()` |
| `.strip() == ""` for blank check              | Catches whitespace-only strings. Fine, but `.strip()` on `None` throws — order of the `or` matters. | Kept, order matters         |

**Known gaps / TODO:**

- [ ] Use `record.get("id")` so a missing key doesn't crash.
- [ ] Return the failing records (or ids), not a pre-formatted `f"..."` string —
      let the caller decide how to present it.
- [ ] Generalise: this is really a "required field is non-empty" check. Could take
      a field name as an argument and reuse it for `name`, `recclass`, etc.
- [ ] Decide what to key the failure on — `name` isn't guaranteed unique/present
      either.

---

### 4.2 `year_check(payload)` — status: working, logic under review

**Goal:**

1. flag records with no `year` key at all;
2. bucket the rest by whether the year is after 1800.

**Current logic:**

```python
for record in payload:
    if "year" not in record.keys():
        no_year_list.append(record['name'])
    elif int(record['year'][:4]) > 1800:
        year_1800_2026.append(record['name'])
    else:
        year_list.append(record['year'])
```

**Trials:**

| Approach                                                    | What happened                                                                                                 | Verdict                           |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| Collect all years first, then loop again to filter `> 1800` | Two passes, second loop was redundant.                                                                        | Dropped (commented out in script) |
| Single pass with `if / elif / else`                         | One loop, three buckets.                                                                                      | **Kept**                          |
| `"year" not in record.keys()`                               | Works. `.keys()` is unnecessary — `"year" not in record` does the same.                                       | Simplify                          |
| `int(record['year'][:4])`                                   | Assumes `year` is always a well-formed string ≥ 4 chars. No guard for `None`, `""`, or a short/garbage value. | Needs fixing                      |

**Known gaps / TODO:**

- [ ] Drop `.keys()` — `"year" not in record`.
- [ ] Handle `year` present but `None` / empty / non-numeric before `int(...)`.
- [ ] Name the magic numbers — what is 1800 protecting against? (pre-1800 records
      are sparse / less reliable?) Add an upper bound check too (future dates,
      typos like `29xx`).
- [ ] `year_1800_2026` is a misleading name — nothing enforces the 2026 upper
      bound yet.
- [ ] Clarify the contract: is "old year" a _failure_ or just a _bucket_? Right
      now it's neither rejected nor quarantined.
- [ ] Return structured data instead of a formatted multi-line string.

---

### 4.3 `mass_check(payload)` — status: stub

**Goal (draft):** flag records where `mass` is missing, non-numeric, `<= 0`, or
absurdly large.

- [ ] Missing key / null / blank
- [ ] `float(mass)` fails → non-numeric
- [ ] `mass <= 0`
- [ ] Decide on an upper sanity bound (largest known meteorite mass ~6×10⁷ g)

---

### 4.4 `coord_check(payload)` — status: stub

**Goal (draft):** validate `reclat` / `reclong` (and cross-check `geolocation`).

- [ ] Both present and numeric
- [ ] `-90 <= lat <= 90`, `-180 <= long <= 180`
- [ ] Flag `0, 0` (null island — common placeholder for missing coords)
- [ ] Do `reclat/reclong` and `geolocation.latitude/longitude` ever disagree?

---

### 4.5 `quarantine_check` / routing — status: stub

**Goal (draft):** collect every failing record from the checks above and write
them to a separate file (`data/quarantine/...`) with a reason attached, so the
main load only sees clean records.

- [ ] Decide the quarantine record shape — original record + list of failed rules?
- [ ] One record can fail multiple checks — dedupe on id.
- [ ] Where does this run — inside `main()` after all checks.

---

## 5. Cross-cutting refactors

Things that apply to the whole script, not one check:

- [ ] **`main()` function** — right now the `with open(...)` block at module level
      does the orchestration. Move it into `def main():` guarded by
      `if __name__ == "__main__":`.
- [ ] **Path handling** — hard-coded absolute path in the script. Use the relative
      path (`data/nasa-json-api/meteor_data.json`) or `pathlib` relative to the
      repo root.
- [ ] **Return values over print strings** — every check returns an `f"..."`
      string right now. Return lists / dicts; let `main()` format the summary.
- [ ] **Load the file once** — pass `data` into each check rather than each check
      re-reading.
- [ ] **Shared helpers** — `is_blank(value)` and `get_field(record, key)` would
      remove repeated `is None or .strip() == ""` logic.
- [ ] **Consistent failure key** — pick one identifier (probably `id`, falling
      back to index) and use it everywhere instead of mixing `name` and `id`.
- [ ] **Logging** — swap `print` for the `logging` module once there's a `main()`.

---

## 6. Open questions

- What's the actual acceptance criteria for a record to be "loadable"? Which
  checks are hard failures vs. soft warnings?
- Should quarantined records be re-processed later, or is quarantine terminal?
- Do the NeoWS records (incremental pipeline) reuse these checks or need their
  own? (README mentions this is undecided.)
