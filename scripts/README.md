# Profile instruments

Run from the repository root with Python 3.10+ (standard library only):

```sh
GITHUB_TOKEN="$(gh auth token)" python3 scripts/build.py
```

The token is used in memory and is never written to generated files. GitHub Actions
uses its built-in `GITHUB_TOKEN`; no personal access token secret is needed.

## Data contract

- `github_stats.py` paginates the public owned-repository REST endpoint and also
  checks `private == false`, `visibility == public`, and the owner. Repository and
  star totals include forks. Followers come from the public user endpoint.
- Language proportions aggregate GitHub language **bytes** across owned public
  repositories excluding forks. They do not measure proficiency or recent work.
  All languages are retained in `assets/stats.json`; the cards show the five
  largest and combine the rest as Other.
- The contribution window includes today and the preceding 364 UTC dates.
  Commits, opened issues, opened PRs, PR reviews, and created repositories come
  from `contributionsCollection`, including contributions to others' repositories.
  Every counted repository must explicitly have `visibility == PUBLIC`. Restricted
  or missing nodes are excluded. The aggregate calendar, global contribution
  totals, and restricted contribution counts are never used.
- Issue, PR, review, and repository connections are fully paginated. First and
  popular contributions are explicitly included. Commit totals come from each
  public repository's contribution connection. A full 100-repository result is
  split into disjoint UTC date ranges; if a single date still hits the cap, the
  build fails instead of publishing incomplete totals. GitHub's attribution and
  indexing rules apply; review contributions represent the most recent review
  per reviewed PR, as defined by GitHub's contribution API.
- Only aggregate public metrics are saved. Failed API requests or GraphQL errors
  fail the build before any generated file is replaced; stale data is not
  silently presented as fresh.

## Rendering and automation

`svg_cards.py` owns the shared palette, SVG drawing helpers, and three card designs.
Biographical content and the stack are taken from the original profile README.
The cards use system fonts, inline CSS, and SVG geometry. No external assets,
JavaScript, or `foreignObject` are required. Motion respects reduced-motion.

`build.py` validates six SVGs with `xml.etree.ElementTree` before writing them and
versions all eight README image references with a UTC timestamp. Both themes use
the same metrics. The Featured Projects table is maintained in README.md.

- `refresh.yml`: daily at 01:30 UTC (09:30 Asia/Shanghai), manual dispatch, or a
  main-branch push changing scripts/the refresh workflow. It commits the cards,
  public JSON snapshot, and README image versions to main. Concurrent refreshes
  queue; bot pushes do not recursively start Actions.
- `snake.yml`: daily at 01:10 UTC (09:10 Asia/Shanghai), manual dispatch, or changes
  to its workflow. `Platane/snk/svg-only@v3` generates both themes and publishes to
  `output`, preserving branch history. The snake is GitHub's displayed calendar,
  which can include anonymized private-activity squares if the profile enables
  them; it is separate from the strictly public-only stats card.

The reference profile was used as an architectural reference (picture elements,
generated assets, daily jobs). The card design and Python implementation are
original to this repository.
