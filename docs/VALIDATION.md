# Validation summary

## Qualified public beta — 1.2.0-beta.1

The public local-download beta was qualified on 2026-09-07 on Windows with Python 3.14 and Node 24. The recorded release evidence includes backend and curriculum regressions, frontend build and browser checks, dependency and secret reviews, fresh package extraction, local smoke checks, hosted CI, and the public prerelease asset. The release is limited to a clean preparation on the same computer; it does not prove installation on independent hardware, another operating system, or a dedicated assistive-technology review.

The release contains 30 available infrastructure lessons and 20 planned units. It does not provide a hosted application, accounts, synchronization, PWA, translations, or complete Docker/VM/cloud laboratories.

## Local release candidate — 1.2.0-beta.2, not yet public

The beta.2 candidate promotes `data-01`…`data-06`, `security-01`…`security-06`, and `agents-01`…`agents-08` into the portable local package. These read-only guided lessons and their closed-choice labs do not execute learner input or change learner progress, calendar, notes, quizzes, completion, or backups.

The package selector uses an explicit allowlist for the twenty authored lesson bodies. Learner data, private `docs/ai` memory, installed dependencies, fixtures, validators, the agent-controller maintenance example, pilot laboratories, unknown future drafts, and sensitive file types remain excluded. The clean-extraction smoke verifies all fifty catalog entries and every guided lesson/lab route. Artifact name, digest and environment metadata are written to `artifacts/release-manifest.json`, outside the portable package.

Current local evidence is recorded in `docs/ai/tasks/2026-09-23-academy-beta2-release.task.json`: 154 backend tests; TypeScript/Vite build; and isolated Chrome coverage at 1440, 390 and 320 px for catalog, lesson and lab loading, keyboard action, disabled submission, feedback, reset, error recovery, accessibility scan and legacy-progress isolation. The candidate is not a public release claim and does not authorize a commit, push, tag, GitHub release, Docker execution, image pull or hosted CI run.

The candidate remains limited to local Windows use and one-computer preparation evidence. It has no independent assistive-technology review, second-computer installation evidence, hosted service, accounts, synchronization, PWA, translations, or complete Docker/VM/cloud labs.
