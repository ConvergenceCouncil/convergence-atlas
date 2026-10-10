# CONVERGENCE production tracking implementation plan

Goal: preserve canonical identities, separate approval from implementation, and track Sunken Temple delivery with repeatable validation.

Scope approved by the user: canon register, Sunken Temple production board, automated registry checks. Execute inline.

Architecture: JSON registers and a linked Markdown board in the existing atlas repository; a dependency-free Python validator runs in GitHub Actions. Full Relic names and gameplay details stay in a separate private deliverable because the connected repository is public. Existing atlas runtime files remain outside this change.

Files: production/canon.json, production/relic-index.json, production/sunken-temple.json, production/README.md, production/SUNKEN_TEMPLE_BOARD.md, scripts/validate_production.py, tests/test_production.py, .github/workflows/production-validation.yml.

Constraints: 157 figure collections × 5 = 785; 115 originals; 40 beast Relics; 20 folklore Relics; 960 total. Source recovery does not confer new canon approval or prove playable implementation. Completed work needs evidence. No unreleased story or image files in the public repository.

Review focus: duplicate/missing IDs; source coverage falsely presented as production completion; approval without a source; broken task dependencies; public records containing private names/details.

- [x] Recover exact registry identities from the Pass 46 source and inspect the v0.10 Sunken Temple package. Record source fingerprints; preserve later override review separately.
- [x] Write failing behavioral tests for duplicate/missing IDs, redaction, approvals, completion evidence, and dependency integrity.
- [x] Implement the validator and seed registers. Run all tests and validate actual data.
- [x] Create linked Sunken Temple issues and a repository board; add a validation workflow with read-only permissions.
- [ ] Review, commit on an isolated branch, open a pull request, verify GitHub checks, and integrate if green. Save the private source-derived registry separately.

Definition of done: registers and board reachable in GitHub, actual seeded data passes validation, deliberate invalid inputs fail, remote checks verified, private details saved separately. A native GitHub Projects board is not exposed by the connected API; use the issue-backed repository board without representing it as a native Project.

Verification: 17 behavioral tests pass; public production validation passes for 960 source-derived identities and 0/8 tested gameplay tasks. Full private name validation deliberately fails on nine duplicate-name groups; REG-001 remains open.

Review: independent reviewer identified field-redaction bypass, unchecked reference approvals/supersessions, and missing private source evidence. All three corrected with rejection tests. Source snapshot and name-audit details saved privately.
