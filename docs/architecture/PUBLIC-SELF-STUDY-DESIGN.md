# Public self-study design

Status: approved local design; no Cloudflare account, resource, secret, or deployment exists.

## Product boundary

The public product is individual self-study. A learner may opt in to an account only to synchronize that learner's progress between devices. The system has no instructor, classroom, invitation, directory, payment, e-mail delivery, analytics, advertising, employer integration, or server-side lab execution.

Portuguese is the complete source locale. Locale selection must fall back to Portuguese when reviewed English or Spanish content is unavailable. SQL, Ansible, and Docker labs are separate local installers; the public web application never accepts or executes a learner command, container, file, URL, credential, or cloud action.

## Runtime split

```text
Browser PWA (local state + offline queue)
       | static lessons / app shell
Cloudflare Pages (future, public)
       | bounded JSON API over HTTPS
Cloudflare Worker (future sync adapter) -- D1 (future learner records)

Windows local app (current FastAPI + SQLite) -- local lab installers
```

The FastAPI application remains the local package runtime and source of learner-facing learning rules. A future Worker is an adapter for the explicitly versioned sync contract; it does not import Python source or run local labs. The browser owns an encrypted-or-plain local cache only according to the local device's storage guarantees; it must always retain an exportable backup and unsent operations during an outage.

## Learner and progress model

`user_id` is opaque. The account presents an optional normalized handle, a password verifier, an offline recovery-code verifier set, timestamps, and a disabled flag. No e-mail address is required or stored. Password and recovery verification use a reviewed, non-reversible, salted KDF implementation compatible with the deployed Worker; raw passwords, recovery codes, tokens, learner notes, and authorization headers never appear in logs.

The canonical learning state is a versioned document containing legacy day namespaces plus `unit_progress` by published unit ID. A sync operation is an immutable, bounded event: `{operation_id, device_id, base_revision, type, payload, created_at}`. `operation_id` is unique per learner and makes retries idempotent. Payloads accept known lesson IDs, finite ratings, boolean lab success, and bounded note text only.

Boolean progress merges monotonically (`false` to `true`). A completed unit cannot be silently reverted by a stale device. Competing note edits retain both versions and present an explicit learner choice; the Worker never chooses a note silently. A conflict response contains only the affected bounded state and revision, never another learner's data.

## D1 schema and retention direction

The future Worker uses migration files, never ad-hoc schema writes. Tables are: `accounts`, `credential_verifiers`, `recovery_codes`, `sessions`, `progress_snapshots`, `progress_operations`, and `login_throttles`. Every learner-owned table has `user_id` as its leading indexed authorization key. `progress_operations` has a unique `(user_id, operation_id)` constraint. Sessions are short-lived, revocable, stored as hashes, and rotate on authentication. Recovery codes are one-time and hashed.

Progress snapshots retain the current bounded state; operations retain only the minimum history needed for replay and conflict recovery. The precise retention interval, deletion workflow, and export format must be set before deployment. Account deletion must export or delete only the requesting learner's state after explicit confirmation; it is not part of the current local increment.

## API and security direction

The future API has only `/auth/register`, `/auth/login`, `/auth/recover`, `/auth/logout`, `/sync/pull`, and `/sync/push` equivalents. Every request has a strict JSON schema, size limit, origin policy, request timeout, per-handle and per-IP throttling, and generic authentication failures. Authorization occurs at every `user_id` query, not in frontend routing. CORS allows only declared Pages origins after deployment; localhost is a separately declared development origin.

Worker secrets are configured outside Git only after explicit approval. Credentials use `PBKDF2-HMAC-SHA-256`, 600,000 iterations, a distinct cryptographically-random 16-byte salt per verifier, and a 32-byte derived result. The stored format is versioned: `pbkdf2-sha256$v1$600000$<base64url-salt>$<base64url-derived-key>`. Password bytes are UTF-8 without application-side normalization or pre-hashing; handles are normalized separately to lower-case ASCII. Recovery codes use the same versioned verifier family, are one-time, and are displayed only at generation. This selection is compatible with Workers Web Crypto, which supports PBKDF2 key derivation, and follows the current OWASP PBKDF2-HMAC-SHA-256 baseline. A cross-runtime test vector is required before deployment. [Workers Web Crypto](https://developers.cloudflare.com/workers/runtime-apis/web-crypto/) and [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) are the current primary references.

## Offline, quotas, and cost controls

The PWA caches versioned static lessons and keeps a bounded local operation queue. It syncs only after explicit sign-in, app resume, a deliberate retry, or a bounded debounce; it never polls continuously. A quota, timeout, 429, 5xx, or offline response leaves operations locally pending and shows a recovery action. It never upgrades a plan, creates a resource, or discards unsynced data.

The free-tier design budgets below current documented ceilings: no more than one pull plus one pushed batch per active session, batches of at most 50 operations or 64 KiB, snapshots under 512 KiB, notes under 12,000 characters, and indexed single-learner queries. Cloudflare's documented free limits are 100,000 Worker requests/day and D1's 5 million read rows/day, 100,000 written rows/day, and 5 GB total storage. Limits must be rechecked immediately before deployment. [Workers limits](https://developers.cloudflare.com/workers/platform/limits/), [D1 pricing](https://developers.cloudflare.com/d1/platform/pricing/).

The local implementation may create neither a remote account nor a network request by default. It exposes account and sync controls only after the learner explicitly supplies a configured HTTPS sync endpoint; no endpoint is committed as a default. A 401, 409, 413, 429, 5xx, timeout, malformed response, or offline state preserves the local exportable progress and reports a retry action. Unsynced operations are capped at 50/64 KiB and never silently dropped. A production deployment must choose and document an operation-retention window, currently proposed as 30 days after successful snapshot compaction, before accepting any learner data.

## Local lab installers

Each installer is separate from the PWA and validates the local operating system, dependency version, disk space, and required virtualization before doing anything. It uses synthetic fixtures, an explicit learner start action, fixed allowlisted commands, no inherited credentials, time/memory/process limits, default-deny network, a visible stop action, and cleanup limited to its own verified directory. Docker image pulls, WSL setup, privilege elevation, cloud use, or host modifications require separate approval and must never be triggered by the web site.

## Rollout sequence

1. Complete and package the local 50-lesson progress increment.
2. Implement locale and PWA shell with local-only storage and export.
3. Implement the Worker-compatible sync contract and local D1 test harness, including migration, authorization, throttle, outage, conflict, and recovery tests.
4. Review the cryptographic parameters, data-retention policy, and deployment gates.
5. Only after explicit approval, create Cloudflare resources, configure secrets, deploy a preview, and validate in a clean VM.
