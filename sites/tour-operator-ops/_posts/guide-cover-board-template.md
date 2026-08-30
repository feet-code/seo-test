---
title: "Tour Guide Scheduling And Substitution Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for small day-tour, activity, and multi-day tour operators, with concrete fields, decision rules, and implementation steps."
productId: "guide-cover-board"
productName: "Guide Cover Board"
generationFingerprint: "0fa8921991b544dcfe7d"
date: "2026-08-29T21:34:11Z"
author:
  name: "John Smith"
---

The most useful tour guide scheduling and substitution template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Tour, departure, and meeting point | Prevents the record from depending on memory or an inbox search | Open the coverage exception against the departure |
| Original guide and exception | Prevents the record from depending on memory or an inbox search | Identify qualified and available guides |
| Required qualification and language | Prevents the record from depending on memory or an inbox search | Offer and confirm the assignment |
| Available candidate guides | Prevents the record from depending on memory or an inbox search | Transfer manifest, access, and resource instructions |
| Confirmed guide and acceptance time | Prevents the record from depending on memory or an inbox search | Verify guide acceptance and publish the operating plan |
| Pay or schedule adjustment | Prevents the record from depending on memory or an inbox search | Open the coverage exception against the departure |
| Manifest and resource handoff | Prevents the record from depending on memory or an inbox search | Identify qualified and available guides |
| Guest notice or cancellation evidence | Prevents the record from depending on memory or an inbox search | Offer and confirm the assignment |

## Suggested statuses

Use workflow statuses that describe reality: **Open The Coverage Exception Against The Departure → Identify Qualified And Available Guides → Offer And Confirm The Assignment → Transfer Manifest Access And Resource Instructions → Verify Guide Acceptance And Publish The Operating Plan**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When an assigned guide becomes unavailable, assign a next action and review date.
- When no qualified guide accepts by the escalation time, assign a next action and review date.
- When the replacement cannot access the current manifest or resources, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- A bilingual guide calls out before a private tour
- A replacement accepts but lacks the vehicle key
- No guide is available before the cancellation notice cutoff

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open guide coverage exception needs one owner and a next review time
- Completion requires recorded evidence that every uncovered departure is accepted by a qualified guide or escalated to a documented operating decision before the guest notice cutoff
- Automated reminders stop after verified completion or a documented closed reason
- Keep the booking, capacity, manifest, guide, and resource platform as the system of record; only necessary coordination data belongs here

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Guide Cover Board workflow concept](/products/guide-cover-board) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Departure Manifest Readiness](/products/departure-manifest-readiness).
