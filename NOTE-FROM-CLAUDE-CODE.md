# Note from Claude Code (sandbox session, `main` branch) — 2026-07-11

Business model correction, confirmed directly by Garry: **free-tier Cloak
Browser is the permanent setup, not a stopgap.**

Each client's container runs its own free-tier Cloak Browser (unlimited
sessions, no license key required). Garry is not buying, reselling, or
centrally budgeting for Cloak Browser access - the product being sold is
the aggregator (dashboard, QC engine, orchestration) built on top of it,
not Cloak Browser itself.

If any spec doc here frames Cloak Browser licensing or per-session cost
as something LeLinc needs to absorb, price around, or plan for centrally,
that's not accurate to the actual business model - please correct it.

`CLOAKBROWSER_LICENSE_KEY` exists as a per-deployment optional environment
variable (a given client could supply their own Pro key if they want one),
but it's not part of LeLinc's own cost structure.

Full context, plus the rest of the working agreement between this session
and your instance, is in `AGENTS.md` on the `main` branch - worth reading
if you haven't, especially the "Resolved: real Cloak Browser" and
"Resolved: Cookie Grant Flow mechanism" sections, since a couple of
things in the specs on this branch (`q-specs`) don't match what's actually
being built on `main` (noVNC, the reverse-proxy login approach, endpoint
path naming). Not trying to overwrite your docs by editing them directly -
flagging it here instead, per the ownership split in `AGENTS.md`.
