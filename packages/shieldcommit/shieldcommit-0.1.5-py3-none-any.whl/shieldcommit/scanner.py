import re
from pathlib import Path
from .patterns import PATTERNS

def scan_text(text):
    """
    Return list of (pattern_name, match_obj) for given text.
    """
    findings = []
    for name, pattern in PATTERNS.items():
        try:
            for m in re.finditer(pattern, text):
                findings.append((name, m))
        except re.error:
            # skip bad regex to avoid crash
            continue
    return findings

def scan_file(path: Path):
    """
    Scan a file and return findings with line numbers and snippets.
    """
    findings = []
    try:
        text = path.read_text(errors="ignore")
    except Exception:
        return findings

    for name, m in scan_text(text):
        start = m.start()
        line_no = text.count("\n", 0, start) + 1
        lines = text.splitlines()
        snippet = lines[line_no - 1][:200] if line_no - 1 < len(lines) else ""
        findings.append({
            "file": str(path),
            "pattern": name,
            "line": line_no,
            "snippet": snippet,
            "match": m.group(0)[:200]
        })

    return findings

def scan_files(paths):
    results = []
    for p in paths:
        p = Path(p)
        if p.is_file():
            results.extend(scan_file(p))
    return results
