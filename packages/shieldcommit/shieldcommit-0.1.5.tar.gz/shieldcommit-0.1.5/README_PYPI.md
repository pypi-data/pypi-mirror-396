# ShieldCommit 🔐

ShieldCommit is a lightweight CLI tool that prevents accidental secret leaks by scanning
Git commits for sensitive information such as AWS keys, API tokens, and credentials.

## 🚀 Features
- Detects hardcoded secrets before commit
- Works as a Git pre-commit hook
- Fast staged-file scanning
- Easy CLI interface
- Zero external dependencies

## 📦 Installation

```bash
pip install shieldcommit
