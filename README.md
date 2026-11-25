# SPA Dashboards

**saintpaulagency.github.io**: one bookmark for every Saint Paul Agency dashboard, report and tool.

- `index.html` is the hub. It's locked with the team password (the same one as the Meta Ads Dashboard).
- `team/monthly-social-review/` is the Monthly Social Review: what SPA delivered on Meta and social for each client each month. It uses the same lock.
- Every other folder is a short, descriptive address that forwards to where the page lives, so the old links keep working:
  - `team/meta-ads-dashboard/` and `team/meta-targeting-map/`
  - `leadership/<client>-google-ads/`
  - `presentations/`, `samples/` and `previews/`

Addresses read *who it's for* / *what it is*, in lowercase with hyphens. New dashboards follow the same pattern.

## How the lock works

Pages are encrypted with a data key. That key is stored only wrapped with the team key (PBKDF2-SHA256, salt and rounds in `tools/lock.json`), so neither the password nor anything readable about clients is in this repo. The page sources (the hub catalog and each month's report data) are kept in `data/source.enc`, encrypted the same way.

A device that ticked "Remember this device" on any team page opens the others straight away, because they're all on this site.

## Building

```
HUB_DATA_KEY=... HUB_WRAPPED_KEY='{"iv":"...","ct":"..."}' python3 tools/build.py [new-month.json]
```

`tools/build.py` explains how to get both keys from an unlocked Meta Ads Dashboard tab. Never commit `HUB_DATA_KEY`.
