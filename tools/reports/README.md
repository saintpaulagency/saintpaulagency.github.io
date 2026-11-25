# Client dashboard snapshots (spa-reports)

Rebuilds the locked copies of the Claude client dashboards that live at saintpaulagency.github.io/spa-reports/
(Borton Volvo, Carlson Toyota, Dahl Honda Stevens Point, Car Donation Foundation). They open with the
SPA Dashboards password, the same lock as the hub. First done Nov 24, 2026 (data through Nov 23).

1. For each dashboard artifact, save its docs with ArtifactData list (`files`, `datasets`, `dash`, with
   `out_dir` = <work>/<client>/docs) and read each dataset's current asset (`/_blob/<id>` in its doc) into
   <work>/<client>/assets. Logo, fonts and d3 come from the CDF artifact into <work>/brand (ids in brandmap.json
   and d3 41ed33ab7e5ddacceca2f9455c81b9d6).
2. `python3 -I rep_build.py <work>/<client> <work>/brand brandmap.json <client> out/<client>.html`
3. `node check.js out/<client>.html <client>` and `node tabs.js <client>...` (from <work>): no errors, no blank figures.
4. `HUB_DATA_KEY=... HUB_WRAPPED_KEY=... python3 -I lock_reports.py ../build.py ../lock.json out/<client>.html site/<folder>/index.html`
   (keys: see ../build.py; the lock screen names no client), then copy into the spa-reports repo and push
   the same commit to main and gh-pages.

Not covered: `cdf-microsoft/` (made for Microsoft Advertising) and `cdf-cpd-levers/` keep their own password.
