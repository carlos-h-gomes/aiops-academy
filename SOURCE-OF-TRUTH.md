# AIOps Academy — Source of Truth

Status: local release candidate pending public upload

Last public version: 1.2.0-beta.1
Candidate version: 1.2.0-beta.2
Reviewed: 2026-09-23

## Project identity and release

AIOps Academy `1.2.0-beta.2` is a Windows-local learning application for individual study. Its local release candidate provides 50 available lessons: 30 legacy infrastructure lessons plus 20 read-only guided lessons across Data, Security, and Agents/processes. It also provides 11 legacy simulated labs, six exam configurations, and 25 library items. It is source code plus a portable package; it is not a hosted service and does not create accounts or synchronize learner data.

The candidate package includes the 20 read-only non-legacy lessons: `data-01`…`data-06`, `security-01`…`security-06`, and `agents-01`…`agents-08`. The exposed guided labs use fixed local definitions; they do not execute learner text, SQL, files, commands, URLs, models, networks, or external tools. None of these lessons alters learner progress, calendar, notes, quiz, completion, or backup behavior. The previous public beta artifact remains the last public release until the candidate is explicitly uploaded.

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

The beta.2 candidate contains the 20 local guided lessons through read-only unit-ID routes and closed-choice labs. Its package allowlist includes only their 20 authored lesson files; learner state, private `docs/ai` memory, installed dependencies, fixtures, validators, optional pilot labs, and sensitive file types remain excluded. Public upload is pending final review of the local release packet.

## Risks and unknowns

The candidate is qualified only for local Windows use with the documented Python and Node prerequisites. It has no independent second-computer installation evidence, dedicated assistive-technology review, hosted application, accounts, synchronization, PWA, translations, or complete Docker/VM/cloud labs. Pilot labs do not reduce these limitations.

## Last qualified evidence

The public beta.1 release evidence and beta.2 candidate evidence are summarized in `docs/VALIDATION.md`. A passing local candidate check does not publish, commit, tag, or upload the new beta.

## Reconciliation rule

When code, generated metadata, documentation, or task records disagree, preserve learner data and the last qualified public beta. Reconcile the conflict before a release claim, a package build, or promotion of planned content. Changes to lesson IDs, progress, or backup compatibility require a separately tested migration.
