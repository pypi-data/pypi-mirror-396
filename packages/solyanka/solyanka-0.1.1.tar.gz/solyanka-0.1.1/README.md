# Solyanka

Toolkit + dataset for transaction-pattern driven synthetic statements and downstream LLM fine-tuning.
This package ships the curated YAML files, their schema, and a tiny loader that apps or notebooks can
use without worrying about file layout.

## Install

```bash
pip install solyanka              # consumers
pip install -e ".[dev]"           # local hacking (tests + linters)
```

## Runtime use

```python
from solyanka import PatternsService

svc = PatternsService()                         # auto-discovers packaged data
general = svc.load_general_patterns()
eea = svc.load_eea_patterns()
thailand = svc.load_country_patterns("Thailand")

# Recommended helper: general + (EEA) + country
bundle = svc.get_country_patterns("Germany")

# Fine-grained slices (e.g., validation scripts)
custom = svc.get_patterns(country="Germany", include="general,eea")

# API-ready dictionaries
payload = svc.get_pattern_dicts(country="Spain")
```

Override the dataset path (e.g., while editing YAML) via `PatternsService(base_dir=Path("./transaction_patterns"))`
or the `TRANSACTION_PATTERNS_DIR` environment variable.

## Layout

- `solyanka/transaction_patterns/data/*.yml` — curated pattern files (`general.yml`, `eea.yml`, `<country>.yml`).
- `solyanka/transaction_patterns/data/schema.json` — JSON Schema enforced by tests/CI.
- `solyanka/transaction_patterns/service.py` — public loader API (keep backward compatible).
- `tests/` — schema regression + loader behaviour.

## Field spec

### Required fields

| Field            | Meaning                                                                                           |
|------------------|---------------------------------------------------------------------------------------------------|
| `title`          | Merchant label. Plain string or template object.                                                   |
| `currency`       | Uppercase ISO 4217 (EUR, USD, GBP, ...).                                                           |
| `amountRange`   | `{min, max}` floats describing the observed local-currency range.                                  |
| `amountFormat`  | Rounding strategy: `n>0` decimals, `0` whole units, `n<0` powers of ten (e.g., `-2` rounds to 100s).|
| `types`          | Non-empty list of lowercase tags (`shopping`, `restaurant`, `transportation`, ...).               |
| `prettyTitle`   | Short merchant label for UI use. Strip cities/countries/punctuation manually (no scripts); follow the documented brand rules (Uber/Amazon/Airbnb/Youtube/Godaddy/Myprotein/Zenni/Bolt/Iherb/Lotus, etc.). |

### Optional fields

| Field                       | Why / how                                                                               |
|-----------------------------|-----------------------------------------------------------------------------------------|
| `weight`                    | Relative selection probability. 100 = baseline, 120–150 very common, 50 niche.          |
| `refundProbability`        | Chance (0–1) that the generator emits a `CARD_REFUND` for this pattern.                 |
| `refundDelayMinHours`/`Max` | Boundaries for automatic refund timing (defaults: 72 / 288 hours).                      |
| `numberOfOccurrences`       | Global cap per statement (useful for rare, one-off merchants).                          |
| `subscriptionFrequencyDays` | Frequency for recurring charges (e.g., 30 for monthly subscriptions).                 |

## Template titles

```yaml
title:
  type: template
  template: "Revolut**{num}* DUBLIN"
  params:
    num:
      generator: random_digits
      length: 4
      zero_pad: true
      globalConstant: true
      transform:
        case: upper
```

### Generators & parameters

| Generator        | Required params | Optional params                | Notes                                            |
|------------------|-----------------|--------------------------------|--------------------------------------------------|
| `random_digits`  | `length`        | `zero_pad` (default `true`)    | digits only; zero_pad keeps leading zeroes       |
| `random_alnum`   | `length`        | `charset`                      | mix of letters/digits; `charset` restricts symbols. The default is `abcdefghijklmnopqrstuvwxyz0123456789`. |
| `choice`         | `options`       | `weights` (same length)        | uniform when weights omitted                     |

Extras:

- `globalConstant: true` — reuse the same generated value across the statement (great for IDs).
- `transform.case`: `upper`, `lower`, or `title`.

## Examples

### Simple grocery merchant

```yaml
- title: "Tesco Express"
  currency: "GBP"
  amountRange: {min: 5.0, max: 50.0}
  amountFormat: 2
  types: ["groceries", "shopping"]
  weight: 120
```

### Subscription service

```yaml
- title: "Netflix.com"
  currency: "EUR"
  amountRange: {min: 13.49, max: 13.49}
  amountFormat: 2
  subscriptionFrequencyDays: 30
  numberOfOccurrences: 10
  types: ["entertainment", "subscription"]
  weight: 300
```

### Template with refund metadata

```yaml
- title:
    type: template
    template: "Airbnb * {code} 662-105-6167"
    params:
      code:
        generator: random_alnum
        length: 12
        charset: "abcdefghijklmnopqrstuvwxyz0123456789"
        transform:
          case: lower
        globalConstant: true
  currency: "USD"
  amountRange: {min: 70.0, max: 900.0}
  amountFormat: 2
  refundProbability: 0.4
  types: ["housing"]
  weight: 700
```

## Pattern authoring workflow

1. Pick the right file (`general.yml`, `eea.yml`, or `<country>.yml`).
2. Study existing entries (Thailand’s file is a good reference for tone + “uglified” merchant names).
3. Choose realistic `amountRange`, `amountFormat`, tags, and weights.
4. Use templates when merchants expose reference numbers.
5. Annotate generated blocks with comments (e.g., `# Generated transaction pattern - online food`).
6. Refresh `prettyTitle` after title tweaks by applying the manual derivation rules (strip city/country noise, drop IDs, canonicalize big brands).
7. Run `pytest` to validate against `schema.json` before committing/publishing.

## Tests & release

```bash
pytest                # validates YAML + loader invariants
python -m build       # optional local artifact check
```

- CI: `.github/workflows/ci.yml` runs pytest on push/PR.
- Release automation: merge PRs into `main` with `major release`, `minor release`, or `patch release` labels to control how `.github/workflows/release-tagger.yml` bumps the version after CI finishes green. No label defaults to a build bump (`v1.2.3` → `v1.2.3.1`, etc.). The workflow updates `pyproject.toml` and tags the commit as `v<version>`.
- PyPI publish: semantic tags (`vMAJOR.MINOR.PATCH` with optional `.<build_or_label>`) trigger `.github/workflows/release.yml`. The release tagger simply creates the tag, so publishing is entirely driven by tag pushes (manual or automated).
- Need to generate new country patterns for a task? See `AGENTS.md` for the full enrichment workflow.

## Pattern preview workflow

Pull requests that touch `solyanka/transaction_patterns/data/**` automatically run
`.github/workflows/pattern-preview.yml`. The workflow uses `python -m solyanka.pattern_preview`
to diff the branch against the PR base, synthesize up to three example transactions from the
touched patterns, and posts a Markdown table comment (including short/pretty titles) back onto the PR so reviewers can eyeball
the new merchants. Preview-only fixtures live under `tests/pattern_preview/` and are injected
via the workflow using the `--extra-patterns` flag so they stay separate from the shipped data.
If the rendered tables grow beyond GitHub’s comment limit, the workflow automatically splits
the output into sequential comments while keeping each pattern block intact.
Run the same command locally to preview the output before pushing changes:

```bash
python -m solyanka.pattern_preview \
  --base-ref origin/main \
  --head-ref HEAD \
  --samples-per-pattern 3 \
  --extra-patterns tests/pattern_preview
```

Conventions: keep YAML human-readable (sorted keys, helpful comments), avoid UUID-looking titles, and update schema/tests whenever the structure changes.

## Purpose recap

Solyanka is the single source of truth for transaction-pattern assets used by the bank-statement
generator and any LLM training pipelines. Treat it like a dataset project: tight validation, small
focused API surface, deterministic releases.
