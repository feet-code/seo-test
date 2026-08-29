---
title: "Self-Storage Delinquency Follow-Up Tracking Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for independent self-storage facilities and small multi-site operators, with concrete fields, decision rules, and implementation steps."
productId: "delinquency-promise-board"
productName: "Delinquency Promise Board"
generationFingerprint: "e6792f9ff583a53ae077"
coverImage: "/assets/blog/preview/cover.jpg"
date: "2026-08-29T21:34:11Z"
author:
  name: "John Smith"
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/dynamic-routing/cover.jpg"
---

The most useful self-storage delinquency follow-up tracking template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Facility, tenant, unit, and lease | Prevents the record from depending on memory or an inbox search | Open the delinquency action from the account ledger |
| Balance and aging date | Prevents the record from depending on memory or an inbox search | Apply the current facility policy and milestone |
| Policy version and current milestone | Prevents the record from depending on memory or an inbox search | Contact the tenant through the approved channel |
| Notice channel and delivery evidence | Prevents the record from depending on memory or an inbox search | Record a payment, promise, dispute, move-out, or escalation |
| Tenant response and promise date | Prevents the record from depending on memory or an inbox search | Verify the ledger and access outcome before closure |
| Manager exception and approval | Prevents the record from depending on memory or an inbox search | Open the delinquency action from the account ledger |
| Access or move-out status | Prevents the record from depending on memory or an inbox search | Apply the current facility policy and milestone |
| Payment evidence or next review | Prevents the record from depending on memory or an inbox search | Contact the tenant through the approved channel |

## Suggested statuses

Use workflow statuses that describe reality: **Open The Delinquency Action From The Account Ledger → Apply The Current Facility Policy And Milestone → Contact The Tenant Through The Approved Channel → Record A Payment Promise Dispute Move Out Or Escalation → Verify The Ledger And Access Outcome Before Closure**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When a balance reaches the next policy milestone, assign a next action and review date.
- When a tenant makes or misses a payment promise, assign a next action and review date.
- When payment, access, or move-out status changes in another system, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- A tenant promises Friday payment after a reminder
- An online payment posts after an access action was queued
- A manager approves a move-out resolution instead of another collection step

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open delinquent tenant action needs one owner and a next review time
- Completion requires recorded evidence that every delinquent account has a policy-based next action, documented tenant response, and verified stop condition
- Automated reminders stop after verified completion or a documented closed reason
- Keep the facility-management, access, lease, and payment platform as the system of record; only necessary coordination data belongs here

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Delinquency Promise Board workflow concept](/products/delinquency-promise-board) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Unit Turn Readiness](/products/unit-turn-readiness).
