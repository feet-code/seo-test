---
title: "Orthodontic Patient Record Transfer Tracking Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for independent orthodontic practices and small specialty dental groups, with concrete fields, decision rules, and implementation steps."
productId: "ortho-record-transfer"
productName: "Orthodontic Record Transfer Desk"
generationFingerprint: "05064823d5a24d24c324"
date: "2026-08-30T04:38:30Z"
author:
  name: "John Smith"
---

The most useful orthodontic patient record transfer tracking template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Record-Transfer Request identifier and source | Prevents the record from depending on memory or an inbox search | Open the record-transfer request from a verified source |
| Customer account site or operating location | Prevents the record from depending on memory or an inbox search | Collect the required inputs and operating evidence |
| Current status version and last change | Prevents the record from depending on memory or an inbox search | Validate readiness and classify material exceptions |
| Required input evidence and received time | Prevents the record from depending on memory or an inbox search | Assign the next action and communicate the decision |
| Exception category impact and decision boundary | Prevents the record from depending on memory or an inbox search | Verify the outcome and close or reschedule the record-transfer request |
| Owner next action and responsible reviewer | Prevents the record from depending on memory or an inbox search | Open the record-transfer request from a verified source |
| Due window escalation time and communication state | Prevents the record from depending on memory or an inbox search | Collect the required inputs and operating evidence |
| Verified outcome closed reason and audit note | Prevents the record from depending on memory or an inbox search | Validate readiness and classify material exceptions |

## Suggested statuses

Use workflow statuses that describe reality: **Open The Record Transfer Request From A Verified Source → Collect The Required Inputs And Operating Evidence → Validate Readiness And Classify Material Exceptions → Assign The Next Action And Communicate The Decision → Verify The Outcome And Close Or Reschedule The Record Transfer Request**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When a new record-transfer request is created or its due window changes, assign a next action and review date.
- When a required input is missing, contradictory, or no longer current, assign a next action and review date.
- When the assigned action fails, changes scope, or reaches its review time, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- A receiving practice reports a missing image
- The request covers only selected dates
- A portal link expires before download

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open record-transfer request needs one owner and a next review time
- Completion requires recorded evidence that every authorized record transfer has a defined scope, secure delivery evidence, and verified receipt or exception
- Automated reminders stop after verified completion or a documented closed reason
- Keep authoritative business, customer, safety, clinical, legal, or compliance data in its approved system of record and expose only necessary coordination fields

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Orthodontic Record Transfer Desk workflow concept](/products/ortho-record-transfer) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Orthodontic Appliance Readiness](/products/ortho-appliance-readiness).
