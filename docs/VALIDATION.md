# Validation summary

## Qualified public beta — 1.2.0-beta.1

The public local-download beta was qualified on 2026-09-07 on Windows with Python 3.14 and Node 24. The recorded release evidence includes backend and curriculum regressions, frontend build and browser checks, dependency and secret reviews, fresh package extraction, local smoke checks, hosted CI, and the public prerelease asset. The release is limited to a clean preparation on the same computer; it does not prove installation on independent hardware, another operating system, or a dedicated assistive-technology review.

The release contains 30 available infrastructure lessons and 20 planned units. It does not provide a hosted application, accounts, synchronization, PWA, translations, or complete Docker/VM/cloud laboratories.

## Public beta — 1.2.0-beta.2

The beta.2 public release promotes `data-01`…`data-06`, `security-01`…`security-06`, and `agents-01`…`agents-08` into the portable local package. These read-only guided lessons and their closed-choice labs do not execute learner input or change learner progress, calendar, notes, quizzes, completion, or backups.

The package selector uses an explicit allowlist for the twenty authored lesson bodies. Learner data, private `docs/ai` memory, installed dependencies, fixtures, validators, the agent-controller maintenance example, pilot laboratories, unknown future drafts, and sensitive file types remain excluded. The clean-extraction smoke verifies all fifty catalog entries and every guided lesson/lab route. Artifact name, digest and environment metadata are written to `artifacts/release-manifest.json`, outside the portable package.

Current release evidence is recorded in `docs/ai/tasks/2026-09-23-academy-beta2-release.task.json`: 154 backend tests; TypeScript/Vite build; and isolated Chrome coverage at 1440, 390 and 320 px for catalog, lesson and lab loading, keyboard action, disabled submission, feedback, reset, error recovery, accessibility scan and legacy-progress isolation. The commit-bound artifact was published as [v1.2.0-beta.2](https://github.com/carlos-h-gomes/aiops-academy/releases/tag/v1.2.0-beta.2) from `25f9aef5402e536541de77f01c1067f509c93faa`, with SHA-256 `4cbf01d3c47cc1fb7bb2e49fae037885db6968e1b366f4a8a317ae2c8d6e4f8b`. This evidence does not authorize Docker execution, image pulls, hosted CI, account creation, Cloudflare configuration, or a later deployment.

The public beta remains limited to local Windows use and one-computer preparation evidence. It has no independent assistive-technology review, second-computer installation evidence, hosted service, accounts, synchronization, PWA, reviewed translations, or complete Docker/VM/cloud labs.

## Unreleased local increment — 50-lesson progress

The additive guided-unit progress flow passed 13 targeted backend tests for closed lab evaluation, unit completion, review, backup v2, restore compatibility, and legacy namespace preservation. The isolated Chrome journey passed at 1440, 390, and 320 px after completing `data-01`; it covers correct lab feedback, evidence entry, completion, responsive rendering, keyboard action, and preservation of the legacy fixture alongside the new `unit_progress` state. This evidence applies only to the local working tree and does not qualify a package, commit, tag, or publication.

## Unreleased local increment — PWA shell and offline study

The frontend production build passed after adding the manifest, service worker registration, visible offline status, and protected static routes. A dedicated isolated-Chrome test installed the service-worker scope, loaded a curriculum page, switched the browser offline, and reopened the cached curriculum shell with the offline status visible. The API static-route test verifies that the built manifest and service worker are delivered from the loopback-only application. The full tracks journey also passed at 1440, 390, and 320 px with service workers deliberately blocked so its synthetic API failure/retry coverage remains deterministic.

The cache is deliberately narrow: successful same-origin reads for course, current progress, curriculum, manuals, and previously opened unit/lab resources may be recovered offline. Writes, backup export/restore, credentials, external links, and synchronization operations are not cached or queued. This is local working-tree evidence only; it does not qualify an installed app on a second computer, a hosted PWA, account sync, or release publication.

## Unreleased local increment — optional account adapter

The future Worker source has a versioned D1 migration and local in-memory tests covering registration, generic failed-login behavior, a five-failure temporary throttle, recovery-code single use, password replacement, session revocation, authenticated pull/push, idempotent operations, calendar settings, checkpoint scores, lab completion, monotonic progress, and explicit conflicts for settings, reviews, and evidence. A two-device in-memory path proves a stale second device can merge objective progress and receives a conflict for competing evidence. The same test proves an exact configured origin receives a valid preflight response while an unlisted origin is rejected. The frontend build and isolated sync-plan test cover HTTPS endpoint validation, full local-progress merge, conflict detection, and bounded batches. The UI has no default endpoint and only makes a remote request after a learner has saved an endpoint, authenticated, and clicked the sync action. A separate Python/Workers compatibility vector verifies the PBKDF2-HMAC-SHA-256 profile. Syntax, the adapter tests, the vector, frontend build, and package-boundary selection passed. A user-authorized browser review verified that a new free Worker preview has one empty D1 `DB` binding, exact loopback-only CORS configuration, and persistent logs/tracing disabled; no company/custom domain, Pages application, user account, migration, adapter-code deployment, or hosted end-to-end test is claimed.

## Candidate local beta — 1.2.0-beta.3

At the candidate working-tree state, the bounded backend suite passed; the frontend production build and isolated Chrome coverage passed at 1440, 390 and 320 px for tracks, library, pace, PWA, account/sync, locale fallback, search, accessibility, retry, offline, and no-overflow journeys; and the local Worker credential, sync-contract, and auth-flow tests passed. The portable package was rebuilt with a clean-extraction smoke test covering the UI, API, 30 legacy lessons, 50-unit curriculum, 20 guided lessons/labs, kit and QA-route exclusion. The generated local release manifest records the archive hash and dependency-lock hashes. This is a local candidate, not a GitHub release or hosted deployment; second-computer installation, hosted end-to-end synchronization, and editorial English/Spanish content remain unvalidated or intentionally unavailable.
