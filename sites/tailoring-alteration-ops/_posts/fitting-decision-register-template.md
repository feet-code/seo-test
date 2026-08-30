---
title: "Tailoring Fitting Change Approval Tracking Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for independent tailoring, alteration, and garment-repair shops, with concrete fields, decision rules, and implementation steps."
productId: "fitting-decision-register"
productName: "Fitting Decision Register"
generationFingerprint: "ef160cc1f1d9a8aef4c5"
date: "2026-08-29T21:59:23Z"
author:
  name: "John Smith"
---

The most useful tailoring fitting change approval tracking template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Customer garment and order | Prevents the record from depending on memory or an inbox search | Prepare the current garment and prior plan |
| Fitting number date and fitter | Prevents the record from depending on memory or an inbox search | Capture fit observations and requested changes |
| Garment measurements and marked locations | Prevents the record from depending on memory or an inbox search | Translate decisions into specific alteration work |
| Customer fit observations | Prevents the record from depending on memory or an inbox search | Confirm price date and customer approval |
| Approved alteration lines and tolerances | Prevents the record from depending on memory or an inbox search | Publish the new version for sewing or next fitting |
| Price and due-date change | Prevents the record from depending on memory or an inbox search | Prepare the current garment and prior plan |
| Customer approval evidence | Prevents the record from depending on memory or an inbox search | Capture fit observations and requested changes |
| Pattern ticket version and next appointment | Prevents the record from depending on memory or an inbox search | Translate decisions into specific alteration work |

## Suggested statuses

Use workflow statuses that describe reality: **Prepare The Current Garment And Prior Plan → Capture Fit Observations And Requested Changes → Translate Decisions Into Specific Alteration Work → Confirm Price Date And Customer Approval → Publish The New Version For Sewing Or Next Fitting**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When a fitting changes the approved alteration plan, assign a next action and review date.
- When price or promised date is affected, assign a next action and review date.
- When the sewer finds instructions inconsistent with garment markings, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- A jacket sleeve change alters button placement
- A dress hem changes after shoes are selected
- A rush request removes time for a planned second fitting

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open fitting decision needs one owner and a next review time
- Completion requires recorded evidence that every fitting produces an agreed current alteration plan, price or date consequence, garment marking reference, and next checkpoint
- Automated reminders stop after verified completion or a documented closed reason
- Keep the tailor-shop POS, customer, measurement, garment, fitting, order, and payment platform as the system of record; only necessary coordination data belongs here

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Fitting Decision Register workflow concept](/products/fitting-decision-register) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Garment Pickup Readiness](/products/garment-pickup-readiness).
