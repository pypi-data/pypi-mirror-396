# KmerFinder (Shim Package)

**KmerFinder is deprecated and has been replaced by SpeciesFinder.**

This package is a *shim layer* that preserves backwards compatibility with
existing workflows that still invoke:

```python
kmerfinder …

python -m kmerfinder

import kmerfinder
```

This shim:

- Emits a clear **deprecation warning**
- Automatically forwards all execution to the new tool: **SpeciesFinder**
- Ensures a smooth migration period for users

The shim package will be maintained for approximately **one year** before removal.

---

