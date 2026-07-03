#!/usr/bin/env python3
"""check_script_safety.py - mechanical risk-pattern scan of a skill package.

Layer 1 of a two-layer safety check: DETECTION is mechanical (this script),
CONVICTION is semantic (the auditing LLM judges each hit in context, per
references/hard-code-vs-llm-judgment.md). A hit is a P1 finding PENDING that
judgment - a documented `rm -rf` example in prose is legitimate (note-only);
the same pattern in a bundled script, or prose instructing the model to run
it, is a real P1. Never auto-delete a flagged line.

Scans:
  code  - scripts/**/* and other code files (full pattern set)
  prose - SKILL.md + references/**/*.md and other .md files (prompt-risk
          subset: dangerous-command instructions + hidden-unicode injection)

Self-exclusion: a file named check_script_safety.py is skipped (its own
pattern table would flag itself forever). The LLM layer still reads it.

Usage: python3 check_script_safety.py "<skill_dir>"
Exit:  0 = clean, 1 = hits printed (findings, not an error), 2 = unreadable
"""
import re
import sys
from pathlib import Path

CODE_EXT = {".py", ".sh", ".bash", ".zsh", ".js", ".ts", ".rb", ".pl", ".ps1"}
EXCLUDE = {"check_script_safety.py"}
EXCERPT = 90

# (class, id, regex, scope)  scope: code | prose | both
PATTERNS = [
    ("exec-remote", "pipe-to-shell",
     re.compile(r"(curl|wget)\b[^\n|]*\|\s*(sudo\s+)?(ba|z|da)?sh\b"), "both"),
    ("exec-remote", "powershell-iex",
     re.compile(r"(?i)\biwr\b[^\n]*\|\s*iex|Invoke-Expression"), "both"),
    ("destructive", "rm-abs-or-home",
     re.compile(r"\brm\s+(-[A-Za-z]+\s+)*-[A-Za-z]*[rR][A-Za-z]*\s+[\"']?"
                r"(~|/(?!tmp/|tmp\b|private/tmp)|\$HOME|\$\{HOME)"), "both"),
    ("destructive", "rm-variable-path",
     re.compile(r"\brm\s+-[A-Za-z]*r[A-Za-z]*f[A-Za-z]*\s+[\"']?\$(?!TMPDIR|TMP\b|\{?SCRATCH)"), "both"),
    ("destructive", "git-force-push",
     re.compile(r"git\s+push\b[^\n]*(\s--force\b|\s-f\b)"), "both"),
    ("destructive", "git-reset-hard",
     re.compile(r"git\s+reset\s+--hard"), "both"),
    ("destructive", "chmod-777",
     re.compile(r"chmod\s+(-R\s+)?0?777\b"), "both"),
    ("privilege", "sudo",
     re.compile(r"(^|[;&|`(]\s*)sudo\s+"), "code"),
    ("credential", "ssh-material",
     re.compile(r"~/\.ssh/|\bid_rsa\b|\bid_ed25519\b"), "both"),
    ("credential", "cloud-creds",
     re.compile(r"~/\.aws/|\.netrc\b|\.config/gh/hosts"), "both"),
    ("credential", "keychain",
     re.compile(r"security\s+find-(generic|internet)-password"), "both"),
    ("credential", "token-literal",
     re.compile(r"\b(sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})\b"), "both"),
    ("credential", "env-file-read",
     re.compile(r"\b(cat|source)\s+[^\n]*\.env\b"), "code"),
    ("exfil", "post-file-out",
     re.compile(r"curl\b[^\n]*(\s-d\s*@|--data-binary\s*@|\s-F\s)[^\n]*https?://"), "both"),
    ("obfuscation", "base64-exec",
     re.compile(r"base64\s+(-d|-D|--decode)\b[^\n]*\|\s*(ba|z)?sh\b"), "both"),
    ("obfuscation", "py-eval-exec",
     re.compile(r"(?<![\w.])(eval|exec)\s*\("), "code"),
    ("obfuscation", "subprocess-shell-true",
     re.compile(r"shell\s*=\s*True"), "code"),
    ("hidden-unicode", "zero-width",
     re.compile("[\\u200b\\u200c\\u200d\\u200e\\u200f\\u2060\\ufeff]"), "prose"),
    ("hidden-unicode", "bidi-override",
     re.compile("[\\u202a-\\u202e\\u2066-\\u2069]"), "prose"),
]


def iter_files(root: Path):
    for f in sorted(root.rglob("*")):
        if not f.is_file() or f.name in EXCLUDE:
            continue
        rel = f.relative_to(root)
        if any(p.startswith(".") or p == "__pycache__" for p in rel.parts):
            continue
        if f.suffix == ".md":
            yield f, "prose"
        elif f.suffix in CODE_EXT or (f.parent.name == "scripts" and f.suffix == ""):
            yield f, "code"


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check_script_safety.py <skill_dir>", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).expanduser().resolve()
    if not (root / "SKILL.md").is_file():
        print(f"[check_script_safety] ERROR: {root}/SKILL.md not found", file=sys.stderr)
        return 2
    hits, counts = [], {}
    for f, kind in iter_files(root):
        try:
            text = f.read_text(encoding="utf-8", errors="replace").lstrip("\ufeff")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for cls, pid, rx, scope in PATTERNS:
                if scope != "both" and scope != kind:
                    continue
                if rx.search(line):
                    hits.append((str(f.relative_to(root)), lineno, cls, pid, line.strip()[:EXCERPT]))
                    counts[cls] = counts.get(cls, 0) + 1
    print(f"[check_script_safety] {root}")
    if not hits:
        print("[check_script_safety] PASS - no risk patterns")
        return 0
    for rel, lineno, cls, pid, excerpt in hits:
        print(f"  {rel}:{lineno}  [{cls}] {pid}   {excerpt}")
    summary = "  ".join(f"{k}={v}" for k, v in sorted(counts.items()))
    print(f"[check_script_safety] {len(hits)} hit(s) - {summary}")
    print("[check_script_safety] detection is mechanical; conviction is the auditor's job "
          "(hard-code-vs-llm-judgment.md) - never auto-delete a flagged line")
    return 1


if __name__ == "__main__":
    sys.exit(main())
