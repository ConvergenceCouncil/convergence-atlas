# CONVERGENCE production tracking

Start with [the Sunken Temple board](SUNKEN_TEMPLE_BOARD.md). Each task links to a GitHub issue and has dependencies and acceptance criteria in `sunken-temple.json`.

## Registers

- `canon.json`: six governing rules with approval sources, plus unresolved exact-reference entries for the protagonist and Roenix. No image has been silently selected or substituted.
- `relic-index.json`: all 960 source-derived IDs, redacted for this public repository. Full names and gameplay details are in a separate private source snapshot.
- `sunken-temple.json`: eight delivery tasks derived from the recovered twelve-beat v0.10 production package. Recovery proves source availability, not compilation or playable implementation.

## Update rules

Production status: `backlog`, `in_progress`, `blocked`, `review`, `tested`. Canon approval status: `approved`, `proposed`, `needs_review`, `superseded`. Never treat either axis as the other. Preserve approval sources and record supersessions. To approve a reference, supply the exact file, its SHA-256 fingerprint, and approval evidence. Visual inspection remains required.

Move a delivery task to `tested` only with inspectable evidence: a build ID, playthrough, asset review, test report or comparable record. Update the JSON and issue together; this board is maintained through reviewed repository changes, not automatically synced to native GitHub Projects.

## Checks

Run `python3 -m unittest discover -s tests -v` and `python3 scripts/validate_production.py`. GitHub Actions runs both on relevant pull requests and pushes. It checks exact expected IDs and category counts, public redaction, documented approvals, dependency integrity and tested-task evidence. It does not evaluate image anatomy or compile Unreal.

For a private workspace, run `python3 scripts/validate_production.py --private-registry /path/to/CONVERGENCE_Private_Relic_Registry.json`. This also checks normalized full-name collisions. The initial source audit flags nine duplicate-name groups; those remain open, with names preserved. A public-index pass does not mean those private-name audit findings are closed.

Scope: 785 figure-linked + 115 original + 40 beast + 20 folklore = 960. This is registry coverage, not overall game completion. No game completion percentage is inferred.
