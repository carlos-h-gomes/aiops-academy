# AIOps Academy — Source of Truth

Status: public beta with a planned local-first web evolution

Last public version: 1.2.0-beta.2
Candidate version: 1.2.0-beta.3
Reviewed: 2026-09-23

## Project identity and release

AIOps Academy `1.2.0-beta.2` is a Windows-local learning application for individual study. Its public beta provides 50 available lessons: 30 legacy infrastructure lessons plus 20 read-only guided lessons across Data, Security, and Agents/processes. It also provides 11 legacy simulated labs, six exam configurations, and 25 library items. It is source code plus a portable package; it is not yet a hosted service and does not yet create accounts or synchronize learner data.

The public beta package includes the 20 read-only non-legacy lessons: `data-01`…`data-06`, `security-01`…`security-06`, and `agents-01`…`agents-08`. The exposed guided labs use fixed local definitions; they do not execute learner text, SQL, files, commands, URLs, models, networks, or external tools. None of these lessons currently alters learner progress, calendar, notes, quiz, completion, or backup behavior.

## Architecture profile

The application is a FastAPI backend and a React/TypeScript/Vite frontend, connected only through `/api/v1`. The current API contract is `artifacts/openapi.json`; directory ownership is in `docs/architecture/DIRECTORY-MAP.md`; the maintained architecture policy is `docs/ai/architecture-policy.json`.

## Authoritative source map

| Fact | Authority |
| --- | --- |
| Available course, manuals, and legacy learning behavior | `backend/content/course.json`, `backend/content/manuals.json`, and `backend/app/services/` |
| Curriculum metadata and planned status | `backend/content/curriculum.json`, `backend/app/schemas/curriculum.py`, and `schemas/curriculum.schema.json` |
| Learner progress and backups | `data/` through `backend/app/repositories/` |
| Local startup and supported use | `preparar.cmd`, `iniciar.cmd`, `launcher.py`, and `docs/USER-MANUAL.md` |
| Architecture and operations | `docs/TECHNICAL-DOCUMENTATION.md` and `docs/architecture/DIRECTORY-MAP.md` |
| Current bounded validation evidence | `docs/VALIDATION.md` and `docs/ai/tasks/2026-09-23-academy-beta2-release.task.json` |
| Portable package boundary | `scripts/package_app.py` and `backend/tests/test_package_app.py` |

## Active work and decisions

The beta.2 public release contains the 20 local guided lessons through read-only unit-ID routes and closed-choice labs. Its package allowlist includes only their 20 authored lesson files; learner state, private `docs/ai` memory, installed dependencies, fixtures, validators, optional pilot labs, and sensitive file types remain excluded.

An unreleased local increment now adds `unit_progress` for the 20 guided lessons without changing legacy day identifiers or namespaces. A correct guided lab sets only that unit's `lab_passed` state; a learner then saves an evidence note, explicitly completes the unit, and receives a local review date. Backup v2 carries this additive state while the restore path accepts v1 backups. The curriculum view schedules all 50 available lessons from the learner's existing pace preference. This working-tree increment has local test evidence but is not yet a public package or release claim.

The same unreleased increment now exposes an installable local PWA. Its service worker caches the application shell and successful safe study reads (`course`, current progress, curriculum, manuals, and previously opened unit/lab views). It never caches writes, exports, restore data, or a synchronization queue. When offline, it shows a visible status and can reopen content previously cached on that device; actions still require the local app to respond. The PWA is locally tested only and is not a hosted deployment or cross-device sync claim.

An unreleased Cloudflare-compatible source adapter now has a versioned D1 migration plus local tests for optional account registration, login throttling, one-time recovery codes, password replacement, session revocation, authenticated pull/push, idempotent operations, and explicit conflicts. It synchronizes bounded learner settings, completions, checkpoint scores, simulated-lab results, reviews, and written evidence; boolean progress and higher checkpoint scores merge safely, while differing preferences, reviews, and evidence require an explicit learner choice. The local settings page exposes opt-in account and sync controls only after the learner saves an HTTPS endpoint; it has no default endpoint and makes no request before that explicit action. The session token is session-only, while a bounded pending batch and endpoint remain local. Under a separate user authorization, a new free Workers preview and a new empty D1 database were created and bound as `DB`; its only application variable permits the loopback origin `http://127.0.0.1:8765`, with persistent Worker logs and tracing disabled. No custom/company domain, route, Pages application, credential, learner account, migration execution, or adapter-code deployment exists.

The approved next product direction is public self-study, not instructor-led learning. The application will add an optional lightweight learner account solely to synchronize that learner's own progress across devices. There are no instructor, administrator, classroom, invitation, learner-directory, payment, analytics, or email-service requirements. Cloudflare Pages plus Workers and D1 is the deployment target; GitHub remains the source and release host. The implementation remains locally runnable. The one authorized free preview is intentionally incomplete: it has no Pages application, migration, published adapter code, learner data, custom domain, or company-domain dependency.

Real SQL, Ansible, and Docker practice remains local-only through bounded installers and preflight checks. The public web application never runs learner commands, containers, or infrastructure. Portuguese is the complete source language. The local Settings page now stores a browser-only language preference; choosing English or Spanish explicitly retains Portuguese until each translation is editorially reviewed, so no lesson is partially machine-translated or sent to a third party.

## Risks and unknowns

The current public beta is qualified only for local Windows use with the documented Python and Node prerequisites. It has no independent second-computer installation evidence, dedicated assistive-technology review, hosted application, accounts, synchronization, reviewed translations, or complete Docker/VM/cloud labs. The public release does not yet include the locally implemented PWA increment. Pilot labs do not reduce these limitations. The approved direction is a scoped evolution, not evidence that those features are already implemented.

## Last qualified evidence

The public beta.1 release evidence and beta.2 release evidence are summarized in `docs/VALIDATION.md`. The beta.2 artifact is commit-bound to `25f9aef5402e536541de77f01c1067f509c93faa`; its GitHub release is `v1.2.0-beta.2`.

## Reconciliation rule

When code, generated metadata, documentation, or task records disagree, preserve learner data and the last qualified public beta. Reconcile the conflict before a release claim, a package build, or promotion of planned content. Changes to lesson IDs, progress, or backup compatibility require a separately tested migration.
