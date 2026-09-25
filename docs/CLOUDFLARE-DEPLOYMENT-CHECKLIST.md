# Cloudflare deployment checklist

Status: the source remains prepared locally. A separately authorized isolated free Worker/D1 preview exists with no custom/company domain, route, Pages application, migration, adapter-code deployment, learner data, secret, or public release. This checklist does not itself authorize any further external action.

## Before a protected deployment approval

- Recheck current official Cloudflare Workers, D1, Pages, and billing limits.
- Choose the exact Pages production origin and any temporary local-development origin. Put only those exact origins in `ALLOWED_ORIGINS`; do not use `*`, wildcards, HTTP production origins, or a reflected request origin.
- Create a reviewed copy of `cloudflare/wrangler.example.toml` outside Git. Replace every `REPLACE_` value only after the resource IDs exist; never commit IDs, tokens, or secrets to this repository.
- Confirm that the Worker has only the `DB` binding and no unreviewed service binding, route, scheduled trigger, secret, analytics, or e-mail integration.
- Confirm the 50-operation / 64 KiB request ceiling, the 512 KiB snapshot ceiling, 12,000-character evidence ceiling, per-IP and per-handle throttles, and the seven-day session lifetime remain acceptable.

## Controlled preview sequence

1. Obtain a specific approval naming the account, Worker, D1 database, Pages project, allowed origins, migration, and preview environment.
2. Create the D1 database and record its identifier only in the approved deployment record.
3. Run the reviewed migration once against that preview database. Verify tables and indexes; do not replay an ad-hoc schema change.
4. Deploy a non-production Worker/Pages preview with `workers_dev = false` and an explicit approved route only if that route is part of the approval.
5. Verify registration, login throttling, recovery-code consumption, logout, a two-device sync, conflict choice, timeout/offline preservation, CORS preflight for an allowed origin, and rejection for an unlisted origin.
6. Export one synthetic learner state, verify no secret appears in logs, and delete the synthetic preview account through an approved cleanup procedure.

## Retention and rollback decision required before learner data

Operations are proposed to be retained for 30 days after successful snapshot compaction. Before accepting real learner data, name an owner, a scheduled reviewed cleanup process, its bounded per-run deletion limit, audit evidence, and an account-deletion/export flow. No cleanup worker or scheduled trigger is included here.

Rollback is source and migration aware: keep the prior Worker version available, stop new traffic before a destructive correction, preserve the learner snapshot/operations for forensic export, and restore only through a reviewed forward migration or approved database recovery. Never use an unreviewed down migration against learner data.

## Production exit evidence

Record the approved deployment reference, Worker and Pages versions, migration version, exact allowed origins, validation results, rollback owner, retention owner, current limit check date, and a clean-device validation result. A local test or template is not production evidence.
