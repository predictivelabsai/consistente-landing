# SKILLS.md — Domain & Email Migration: consistente.tech

Operational handoff so a future session (possibly on another machine) can resume and
complete the IONOS email setup and the later registrar transfer.

> **Credentials are NOT in this repo.** They live in `.secrets/credentials.yaml`, which is
> gitignored and stays local. On a new machine, re-provide the IONOS and Namecheap logins
> in-session and recreate that file. Never commit credentials to this repo.

## Goal
1. **Now:** stand up 4 email addresses on `consistente.tech` using IONOS (cheaper inboxes).
2. **Later (after 2026-07-08):** transfer the domain registrar Namecheap → IONOS.

## Key facts
- Domain `consistente.tech` registered **2026-05-09**, expires 2027-05-09, auto-renew ON.
- **ICANN 60-day lock**: registrar transfer not possible until **~2026-07-08**.
- Registrar: **Namecheap** (user `kaljuvee`, registrant email `domains@founderscap.co.uk`).
- IONOS target contract: **`17404409` (IONOS Premium)**; Mail Basic package lives on it.
- Landing site is a single apex record: `A @ → 72.62.88.13` (no `www`, no AAAA).

## Status as of 2026-06-17 (email setup, in progress)
- ✅ Namecheap nameservers switched to **IONOS Custom DNS**:
  `ns1045.ui-dns.com`, `ns1045.ui-dns.de`, `ns1045.ui-dns.org`, `ns1045.ui-dns.biz`.
- ✅ `consistente.tech` added to IONOS as **external domain** on contract `17404409`.
- ✅ DNS delegation has propagated to public resolvers.
- ⏳ IONOS still shows the domain **"verification pending / not in use"** (backend lag).
- 🔴 Apex `consistente.tech` currently returns **no A record** (site temporarily down) because
  IONOS's zone is empty and IONOS blocks DNS editing until the domain is "active".
  (User accepted this brief gap; site is non-critical.)

## Resume checklist (do these in order)
1. **Confirm domain is active in IONOS.** Go to Domains & SSL → `consistente.tech` → details,
   click **"Check now"** until status is "in use" / the domain's checkbox is enabled.
   - Verify externally: `dig +short NS consistente.tech` should return the `ns1045.ui-dns.*` set.
2. **Restore the website.** In the IONOS DNS zone for `consistente.tech`, add: `A  @  → 72.62.88.13`.
   - Verify: `dig +short A consistente.tech @8.8.8.8` returns `72.62.88.13`.
3. **Create 3 real mailboxes** (Email → contract `17404409` → "Create another mailbox" → **Mail Basic**).
   Passwords are pre-generated in `.secrets/credentials.yaml` → `email_setup.passwords`.
   For each, also add the forward under "Forward e-mails":
   - `julian@consistente.tech` → forward to `kaljuvee@gmail.com`
   - `jaan@consistente.tech`   → forward to `ehlvest@gmail.com`
   - `oleg@consistente.tech`   → forward to `oleg.kim@gmail.com`
4. **Create the forwarder** (Create email → **Email forwarding**):
   - `info@consistente.tech` → `julian@`, `jaan@`, `oleg@` (all three)
5. **Verify email.** IONOS auto-adds MX/SPF/DKIM to the zone once mailboxes exist.
   Send/receive a test; confirm SPF + DKIM pass. Confirm each forward delivers to its gmail.

### Fallback if IONOS verification stays stuck
Revert Namecheap nameservers to **BasicDNS** to bring the landing page back up immediately,
then either retry the external-domain setup or wait for the registrar transfer (step below).

## Later: registrar transfer (on/after 2026-07-08)
1. **Namecheap** (Domain → Sharing & Transfer): turn **Domain Lock OFF**, disable WhoisGuard,
   request the **EPP/Auth code** (emailed to `domains@founderscap.co.uk`); save it to
   `.secrets/credentials.yaml` → `domain.auth_code`.
2. **IONOS**: Domains → **Transfer domain to IONOS** → `consistente.tech` + auth code,
   bill to contract `17404409`. Approve the transfer email; optionally approve in Namecheap to skip the wait.
3. After transfer: re-enable lock + privacy at IONOS; cancel Namecheap auto-renew.
