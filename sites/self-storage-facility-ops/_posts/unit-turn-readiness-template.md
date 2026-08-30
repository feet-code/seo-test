---
title: "Self-Storage Move-Out Inspection And Unit Turn Tracking Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for independent self-storage facilities and small multi-site operators, with concrete fields, decision rules, and implementation steps."
productId: "unit-turn-readiness"
productName: "Unit Turn Readiness"
generationFingerprint: "89066ee4c605764d0286"
coverImage: "/assets/blog/preview/cover.jpg"
date: "2026-08-29T21:34:11Z"
author:
  name: "John Smith"
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/dynamic-routing/cover.jpg"
---

The most useful self-storage move-out inspection and unit turn tracking template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Facility and unit | Prevents the record from depending on memory or an inbox search | Confirm tenant move-out and possession |
| Tenant move-out and key or access return | Prevents the record from depending on memory or an inbox search | Inspect condition and capture evidence |
| Inspection time and inspector | Prevents the record from depending on memory or an inbox search | Assign cleaning, repair, or removal work |
| Condition photos and findings | Prevents the record from depending on memory or an inbox search | Reconcile charges, access, and unit status |
| Cleaning or repair tasks | Prevents the record from depending on memory or an inbox search | Verify readiness and publish availability |
| Property-left-behind decision | Prevents the record from depending on memory or an inbox search | Confirm tenant move-out and possession |
| Final account and access status | Prevents the record from depending on memory or an inbox search | Inspect condition and capture evidence |
| Rentable time or hold reason | Prevents the record from depending on memory or an inbox search | Assign cleaning, repair, or removal work |

## Suggested statuses

Use workflow statuses that describe reality: **Confirm Tenant Move Out And Possession → Inspect Condition And Capture Evidence → Assign Cleaning Repair Or Removal Work → Reconcile Charges Access And Unit Status → Verify Readiness And Publish Availability**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When a tenant reports move-out or access ends, assign a next action and review date.
- When inspection finds damage, property, or unresolved access, assign a next action and review date.
- When all work closes but the unit is not yet available online, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- A unit is empty but the lock and access record remain active
- Inspection finds shelving that must be removed
- Cleaning finishes Friday but web availability still shows occupied

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open unit-turn task needs one owner and a next review time
- Completion requires recorded evidence that every vacated unit is inspected, cleared, reconciled, and published as rentable or held with a named reason
- Automated reminders stop after verified completion or a documented closed reason
- Keep the facility-management, access, lease, and payment platform as the system of record; only necessary coordination data belongs here

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Unit Turn Readiness workflow concept](/products/unit-turn-readiness) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Delinquency Promise Board](/products/delinquency-promise-board).
