# Interactive globe

The public home and `/universidades` explorer use a client-only, dynamically loaded Globe.GL renderer. Country geometry is served locally from `/maps/countries.geojson` (Natural Earth, world-atlas `countries-110m.json`, converted with topojson-client). Natural Earth geography is public domain. No external texture, map tile or geocoding service is called at runtime.

Versioned institutional locations are in `data/university-locations.json`, validated by `lib/locations.ts`. City precision denotes an approximate city point. Institutional coordinates do not certify the campus where exchange classes are offered. Source links and notes accompany selected destinations. Missing coordinates leave the institution in the accessible list without a fabricated pin.

Filters use GET parameters `q`, `curso` and `elegiveis=1`. Selecting a course alone does not hide other institutions; the eligibility checkbox applies the COI course flag. With all courses selected, the checkbox includes institutions eligible for at least one course. Eligibility is independent from syllabus affinity or approval.

The globe accepts dragging and pin selection. It never auto-rotates; camera focus transitions are disabled under reduced motion. Scroll zoom is disabled. ResizeObserver sizes the canvas, while visibility observers pause offscreen/hidden rendering. Unmount disposes WebGL resources. WebGL failure leaves the complete list and university links usable.

Manual checks: home/explorer at desktop and narrow viewport; drag and select a pin; select a list row with keyboard; toggle list then select a row; combine text, course and eligibility; zero matches; disable WebGL; reduced motion; follow coordinate source and university links. Browser automation was unavailable during initial implementation; visual acceptance remains a manual check.

Map credits: world-atlas 2.0.2 (ISC license), https://github.com/topojson/world-atlas; Natural Earth, public domain, https://www.naturalearthdata.com/about/terms-of-use/. Geographic boundaries are illustrative and do not establish territorial claims.
