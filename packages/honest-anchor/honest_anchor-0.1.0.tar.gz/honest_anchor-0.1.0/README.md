# ⚓ Honest Anchor

**git commit for your IP**

Timestamp your files to Bitcoin in 10 seconds. Prove prior art. Forever.

```bash
pip install honest-anchor

anchor init
anchor commit my-brilliant-algorithm.py

✓ Anchored to Bitcoin. Proof ready in 1 hour.
```

## Why?

- 🛡️ **Prove prior art** - Before someone patents your idea
- 📜 **Legal-grade timestamps** - Admissible in court
- 🔗 **Immutable Bitcoin proof** - Can't be faked or deleted
- 🆓 **Free for open source** - We love OSS

## How it works

1. Your file is hashed (SHA256)
2. Hash is submitted to Bitcoin via [OpenTimestamps](https://opentimestamps.org)
3. Bitcoin block confirms your timestamp (~1-2 hours)
4. You have permanent proof your file existed at that time

```
Your Code → SHA256 Hash → Bitcoin Block → Forever
```

## Installation

```bash
pip install honest-anchor
```

Requires Python 3.8+

## Quick Start

```bash
# Initialize in your project
anchor init

# Anchor a file
anchor commit README.md

# Anchor with a note
anchor commit -m "Initial algorithm design" algo.py

# Check status
anchor status

# Verify a file hasn't changed
anchor verify README.md

# View history
anchor history
```

## Commands

| Command | Description |
|---------|-------------|
| `anchor init` | Initialize `.anchor/` directory |
| `anchor commit <file>` | Timestamp a file to Bitcoin |
| `anchor commit --all` | Timestamp all matching files |
| `anchor status` | Show pending/confirmed anchors |
| `anchor verify <file>` | Verify file hasn't changed |
| `anchor history` | Show all anchored files |
| `anchor info <file>` | Detailed info about a file |

## Configuration

Edit `.anchor/config.yml`:

```yaml
# Files to auto-anchor
auto_anchor:
  - "*.md"
  - "*.py"
  - "!node_modules/**"

# Your information
author: "Your Name"
email: "you@example.com"
license: "MIT"
```

## Git Integration

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
anchor commit --staged --auto
```

## What this proves

✅ Your file **existed** at this specific time
✅ Your file **hasn't changed** since then
✅ You have **cryptographic proof** anchored to Bitcoin

## What this doesn't prove

❌ You **wrote** the file (authorship)
❌ You **own** the IP (ownership)
❌ This is a **patent** (legal protection)

*For full legal protection, consult an IP attorney.*

## Pricing

| Plan | Price | Features |
|------|-------|----------|
| **Free** | $0 | 10 files/month |
| **Pro** | $9/mo | Unlimited files |
| **Team** | $29/mo | 5 users, dashboard |
| **Enterprise** | $99/mo | API, legal exports |

**Free forever for open source projects!**

## How is this different from...

**Git commits?**
Git timestamps can be faked. Bitcoin can't.

**Wayback Machine?**
Only works for public websites. Anchor works for any file.

**Notary?**
Expensive, slow, requires physical presence. Anchor is instant and free.

**Patents?**
Patents cost $10,000+ and take years. Anchor is free and instant.
(But Anchor proves prior art, which can invalidate patents!)

## Tech

- Bitcoin timestamping via [OpenTimestamps](https://opentimestamps.org)
- Multiple calendar servers for redundancy
- SHA256 hashing
- Local proof storage

## License

BSL-1.1 (Business Source License)

Free for personal and open source use.
Commercial use requires a license.

## Made by

[Stellanium Ltd](https://stellanium.io) - Building honest AI tools.

---

*"Your code deserves a timestamp."*
