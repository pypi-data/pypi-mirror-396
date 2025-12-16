from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import subprocess
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Set, Tuple

import yaml

PATTERNS_DIR = Path("solyanka/transaction_patterns/data")
_HUNK_RE = re.compile(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
COMMENT_CHAR_LIMIT = 65000


@dataclass
class PatternInfo:
    file_path: Path
    index: int
    data: Dict[str, Any]


@dataclass
class PatternSample:
    title: str
    amount: float
    amountFormat: int
    currency: str
    source_file: Path
    pattern_index: int
    prettyTitle: str | None = None

    @property
    def amount_display(self) -> str:
        return format_amount(self.amount, self.amountFormat, self.currency)

    @property
    def label(self) -> str:
        return f"{self.source_file}#{self.pattern_index + 1}"


@dataclass(frozen=True)
class PatternTarget:
    absolute: Path
    relative: Path


class PatternPreviewer:
    """Generate deterministic example transactions for touched patterns."""

    def __init__(
        self,
        repo_root: str | Path = ".",
        base_ref: str = "origin/main",
        head_ref: str = "HEAD",
        pattern_paths: Sequence[str | Path] | None = None,
    ) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.base_ref = base_ref
        self.head_ref = head_ref
        self.pattern_targets: List[PatternTarget] = []
        seen: Set[str] = set()
        raw_paths = list(pattern_paths or [PATTERNS_DIR])
        for raw_path in raw_paths:
            candidate = Path(raw_path)
            if not candidate.is_absolute():
                candidate = (self.repo_root / candidate).resolve()
            if not candidate.exists():
                continue
            try:
                relative = candidate.relative_to(self.repo_root)
            except ValueError:
                continue
            key = relative.as_posix()
            if key in seen:
                continue
            seen.add(key)
            self.pattern_targets.append(PatternTarget(absolute=candidate, relative=relative))

    def generate_preview(
        self,
        *,
        max_total_samples: int | None = None,
        samples_per_pattern: int = 3,
    ) -> Dict[str, Any]:
        changed_files = self._collect_changed_pattern_files()
        changed_patterns: List[PatternInfo] = []
        for file_path in changed_files:
            changed_patterns.extend(self._collect_patterns_for_file(file_path))
        samples = self._generate_samples(
            changed_patterns,
            max_total_samples=max_total_samples,
            samples_per_pattern=samples_per_pattern,
        )
        markdown_chunks = build_markdown_chunks(
            samples,
            changed_files,
            samples_per_pattern,
            max_total_samples,
            COMMENT_CHAR_LIMIT,
        )
        return {
            "changed_files": [str(path) for path in changed_files],
            "patterns_considered": len(changed_patterns),
            "samples": [
                {
                    "title": sample.title,
                    "prettyTitle": sample.prettyTitle,
                    "amount": sample.amount,
                    "currency": sample.currency,
                    "display_amount": sample.amount_display,
                    "source_file": str(sample.source_file),
                    "pattern_index": sample.pattern_index,
                }
                for sample in samples
            ],
            "markdown": markdown_chunks[0] if markdown_chunks else "",
            "markdown_chunks": markdown_chunks,
        }

    def _collect_changed_pattern_files(self) -> List[Path]:
        if not self.pattern_targets:
            return []
        cmd = [
            "git",
            "diff",
            "--name-only",
            "--diff-filter=ACMR",
            f"{self.base_ref}...{self.head_ref}",
            "--",
        ]
        cmd.extend(str(target.relative) for target in self.pattern_targets)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.repo_root,
            check=False,
        )
        if result.returncode not in (0, 1):
            raise RuntimeError(f"Failed to collect changed files: {result.stderr.strip()}")
        files = [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]
        return sorted({path for path in files if (self.repo_root / path).exists()})

    def _collect_patterns_for_file(self, path: Path) -> List[PatternInfo]:
        full_path = (self.repo_root / path).resolve()
        if not full_path.exists():
            return []
        changed_lines = _detect_changed_lines(
            path,
            base_ref=self.base_ref,
            head_ref=self.head_ref,
            repo_root=self.repo_root,
        )
        if not changed_lines:
            return []
        blocks = _enumerate_pattern_blocks(full_path)
        try:
            data = yaml.safe_load(full_path.read_text(encoding="utf-8")) or []
        except yaml.YAMLError:
            return []
        pattern_infos: List[PatternInfo] = []
        for idx, (block, pattern) in enumerate(zip(blocks, data)):
            if not isinstance(pattern, dict):
                continue
            if _block_intersects(block, changed_lines):
                pattern_infos.append(PatternInfo(path, idx, pattern))
        return pattern_infos

    def _generate_samples(
        self,
        patterns: Sequence[PatternInfo],
        *,
        max_total_samples: int | None,
        samples_per_pattern: int,
    ) -> List[PatternSample]:
        per_pattern_limit = max(1, samples_per_pattern)
        samples: List[PatternSample] = []
        seen_titles: set[str] = set()
        for info in patterns:
            pattern_seed = _pattern_seed(info)
            rng = random.Random(pattern_seed)
            attempts = 0
            produced_for_pattern = 0
            while produced_for_pattern < per_pattern_limit and attempts < per_pattern_limit * 4:
                attempts += 1
                title = render_title(info.data.get("title", ""), rng)
                title_clean = title.strip()
                if not title_clean or title_clean in seen_titles:
                    continue
                amount = generate_amount(info.data, rng)
                raw_pretty = info.data.get("prettyTitle")
                prettyTitle = str(raw_pretty).strip() if isinstance(raw_pretty, str) else ""
                sample = PatternSample(
                    title=title_clean,
                    amount=amount,
                    amountFormat=int(info.data.get("amountFormat", 2)),
                    currency=str(info.data.get("currency", "")).strip().upper(),
                    source_file=info.file_path,
                    pattern_index=info.index,
                    prettyTitle=prettyTitle or None,
                )
                seen_titles.add(title_clean)
                samples.append(sample)
                produced_for_pattern += 1
                if max_total_samples is not None and len(samples) >= max_total_samples:
                    return samples
        return samples


def _pattern_seed(info: PatternInfo) -> int:
    # Keep deterministic per pattern, stable across runs.
    payload = json.dumps(
        {
            "file": str(info.file_path),
            "index": info.index,
            "title": info.data.get("title"),
            "amountRange": info.data.get("amountRange"),
            "types": info.data.get("types"),
        },
        sort_keys=True,
        default=str,
    )
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def _detect_changed_lines(
    relative_path: Path,
    *,
    base_ref: str,
    head_ref: str,
    repo_root: Path,
) -> set[int]:
    cmd = [
        "git",
        "diff",
        "--unified=0",
        f"{base_ref}...{head_ref}",
        "--",
        str(relative_path),
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=repo_root,
        check=False,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(f"Failed to diff {relative_path}: {result.stderr.strip()}")
    changed: set[int] = set()
    current_line = None
    for line in result.stdout.splitlines():
        if line.startswith("@@"):
            match = _HUNK_RE.match(line)
            if not match:
                current_line = None
                continue
            start = int(match.group(1))
            current_line = start
        elif current_line is not None and line.startswith("+") and not line.startswith("+++"):
            changed.add(current_line - 1)
            current_line += 1
        elif current_line is not None and line.startswith(" ") and not line.startswith("\\"):
            current_line += 1
        elif current_line is not None and line.startswith("-") and not line.startswith("---"):
            continue
    return changed


def _enumerate_pattern_blocks(relative_path: Path) -> List[range]:
    lines = relative_path.read_text(encoding="utf-8").splitlines()
    blocks: List[range] = []
    current_start = None
    for idx, line in enumerate(lines):
        if line.startswith("- "):
            if current_start is not None:
                blocks.append(range(current_start, idx))
            current_start = idx
    if current_start is not None:
        blocks.append(range(current_start, len(lines)))
    return blocks


def _block_intersects(block: range, changed_lines: Set[int]) -> bool:
    if not changed_lines:
        return False
    for line in block:
        if line in changed_lines:
            return True
    return False


def render_title(raw_title: Any, rng: random.Random) -> str:
    if isinstance(raw_title, str):
        return raw_title
    if not isinstance(raw_title, dict):
        return str(raw_title)
    if raw_title.get("type") != "template":
        return str(raw_title)
    template = str(raw_title.get("template", ""))
    params = raw_title.get("params") or {}
    rendered: Dict[str, str] = {}
    for key, spec in params.items():
        rendered[key] = _render_template_param(spec or {}, rng)
    try:
        return template.format(**rendered)
    except Exception:  # noqa: BLE001
        return template


def _render_template_param(spec: Dict[str, Any], rng: random.Random) -> str:
    generator = spec.get("generator")
    if generator == "random_digits":
        length = int(spec.get("length", 1))
        max_value = 10**length - 1
        value = rng.randint(0, max_value)
        if spec.get("zero_pad", True):
            return str(value).zfill(length)
        return str(value)
    if generator == "random_alnum":
        length = int(spec.get("length", 1))
        charset = spec.get("charset") or "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return "".join(rng.choice(list(charset)) for _ in range(length))
    if generator == "choice":
        options = spec.get("options") or []
        if not options:
            return ""
        weights = spec.get("weights")
        if weights and len(weights) == len(options):
            total = sum(weights)
            pick = rng.uniform(0, total)
            upto = 0.0
            for option, weight in zip(options, weights):
                upto += weight
                if pick <= upto:
                    return str(option)
            return str(options[-1])
        return str(rng.choice(options))
    value = spec.get("value")
    return str(value) if value is not None else ""


def generate_amount(pattern: Dict[str, Any], rng: random.Random) -> float:
    amountRange = pattern.get("amountRange") or {}
    amount_min = float(amountRange.get("min", 0.0))
    amount_max = float(amountRange.get("max", amount_min))
    if amount_min == amount_max:
        value = amount_min
    else:
        value = rng.uniform(amount_min, amount_max)
    amountFormat = int(pattern.get("amountFormat", 2))
    if amountFormat >= 0:
        return round(value, amountFormat)
    step = 10 ** abs(amountFormat)
    return round(value / step) * step


def format_amount(amount: float, amountFormat: int, currency: str) -> str:
    currency_clean = currency.strip().upper()
    if amountFormat > 0:
        formatted = f"{amount:.{amountFormat}f}"
    else:
        formatted = f"{int(round(amount))}"
    return f"{formatted}{currency_clean}"


def build_markdown_chunks(
    samples: Sequence[PatternSample],
    changed_files: Sequence[Path],
    samples_per_pattern: int,
    max_total_samples: int | None,
    comment_char_limit: int | None = COMMENT_CHAR_LIMIT,
) -> List[str]:
    if not samples:
        if changed_files:
            files_line = ", ".join(str(p) for p in changed_files)
            return [
                "### Transaction Pattern Preview\n\n"
                f"Detected changes in: {files_line}\n\n"
                "No transaction titles were generated (only metadata or comments changed)."
            ]
        return ["### Transaction Pattern Preview\n\nNo transaction pattern changes detected."]

    limit_line = f"Showing up to {samples_per_pattern} unique titles per pattern."
    if max_total_samples:
        limit_line = (
            f"{limit_line} Capped at {max_total_samples} total "
            f"{'entry' if max_total_samples == 1 else 'entries'}."
        )

    groups: OrderedDict[Tuple[Path, int], List[PatternSample]] = OrderedDict()
    for sample in samples:
        key = (sample.source_file, sample.pattern_index)
        groups.setdefault(key, []).append(sample)

    files_line = ", ".join(str(p) for p in changed_files)

    def _header_lines(first_chunk: bool) -> List[str]:
        heading = "### Transaction Pattern Preview"
        if not first_chunk:
            heading += " (cont.)"
        header = [heading, ""]
        if files_line:
            header.append(f"Detected changes in: {files_line}")
        else:
            header.append("No transaction pattern changes detected.")
        header.extend([limit_line, ""])
        return header

    def _block_lines(group_label: str, group_samples: Sequence[PatternSample]) -> List[str]:
        block = [f"**{group_label}**", "", "| Title | Pretty title | Amount |", "| --- | --- | --- |"]
        for sample in group_samples:
            title_cell = _escape_table_cell(sample.title)
            short_cell = _escape_table_cell(sample.prettyTitle or sample.title)
            block.append(f"| {title_cell} | {short_cell} | {sample.amount_display} |")
        block.append("")
        return block

    def _lines_length(lines: Sequence[str]) -> int:
        if not lines:
            return 0
        return len("\n".join(lines))

    chunks: List[str] = []
    base_header = _header_lines(True)
    current_lines = list(base_header)
    chunk_has_blocks = False
    for idx, ((source_file, pattern_index), group_samples) in enumerate(groups.items()):
        label = f"{source_file}#{pattern_index + 1}"
        block = _block_lines(label, group_samples)
        candidate_lines = current_lines + block
        if (
            comment_char_limit
            and _lines_length(candidate_lines) > comment_char_limit
            and chunk_has_blocks
        ):
            chunks.append("\n".join(current_lines).rstrip())
            current_lines = _header_lines(False)
            chunk_has_blocks = False
            candidate_lines = current_lines + block
        current_lines.extend(block)
        chunk_has_blocks = True
    if current_lines:
        chunks.append("\n".join(current_lines).rstrip())
    return chunks


def _escape_table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br />")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate sample transactions for touched patterns.")
    parser.add_argument("--repo-root", default=".", help="Repository root (default: current directory)")
    parser.add_argument("--base-ref", default="origin/main", help="Base ref or commit for diff (default: origin/main)")
    parser.add_argument("--head-ref", default="HEAD", help="Head ref or commit for diff (default: HEAD)")
    parser.add_argument(
        "--max-total-samples",
        type=int,
        default=0,
        help="Maximum number of samples across all patterns (0 disables the cap).",
    )
    parser.add_argument("--samples-per-pattern", type=int, default=3, help="Samples to attempt per pattern")
    parser.add_argument(
        "--extra-patterns",
        action="append",
        default=[],
        help="Additional directories or files containing transaction patterns (relative to repo root).",
    )
    parser.add_argument("--output-file", help="Optional path to write JSON results")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    max_total = args.max_total_samples or None
    pattern_inputs: List[Path] = [PATTERNS_DIR]
    if args.extra_patterns:
        pattern_inputs.extend(Path(p) for p in args.extra_patterns)
    previewer = PatternPreviewer(
        repo_root=args.repo_root,
        base_ref=args.base_ref,
        head_ref=args.head_ref,
        pattern_paths=pattern_inputs,
    )
    result = previewer.generate_preview(
        max_total_samples=max_total,
        samples_per_pattern=args.samples_per_pattern,
    )
    chunks = result.get("markdown_chunks") or []
    for idx, chunk in enumerate(chunks):
        if idx:
            print("")
        print(chunk)
    if args.output_file:
        Path(args.output_file).write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
