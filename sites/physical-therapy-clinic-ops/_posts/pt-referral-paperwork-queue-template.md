---
title: "Physical Therapy Referral And Authorization Paperwork Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for independent physical therapy clinics and small rehabilitation practices, with concrete fields, decision rules, and implementation steps."
productId: "pt-referral-paperwork-queue"
productName: "PT Referral Paperwork Queue"
generationFingerprint: "6369a6363323f6f23fc1"
date: "2026-08-30T04:38:30Z"
author:
  name: "John Smith"
---

The most useful physical therapy referral and authorization paperwork template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Referral Record identifier and source | Prevents the record from depending on memory or an inbox search | Open the referral record from a verified source |
| Customer account site or operating location | Prevents the record from depending on memory or an inbox search | Collect the required inputs and operating evidence |
| Current status version and last change | Prevents the record from depending on memory or an inbox search | Validate readiness and classify material exceptions |
| Required input evidence and received time | Prevents the record from depending on memory or an inbox search | Assign the next action and communicate the decision |
| Exception category impact and decision boundary | Prevents the record from depending on memory or an inbox search | Verify the outcome and close or reschedule the referral record |
| Owner next action and responsible reviewer | Prevents the record from depending on memory or an inbox search | Open the referral record from a verified source |
| Due window escalation time and communication state | Prevents the record from depending on memory or an inbox search | Collect the required inputs and operating evidence |
| Verified outcome closed reason and audit note | Prevents the record from depending on memory or an inbox search | Validate readiness and classify material exceptions |

## Suggested statuses

Use workflow statuses that describe reality: **Open The Referral Record From A Verified Source → Collect The Required Inputs And Operating Evidence → Validate Readiness And Classify Material Exceptions → Assign The Next Action And Communicate The Decision → Verify The Outcome And Close Or Reschedule The Referral Record**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When a new referral record is created or its due window changes, assign a next action and review date.
- When a required input is missing, contradictory, or no longer current, assign a next action and review date.
- When the assigned action fails, changes scope, or reaches its review time, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- A referral omits a required provider detail
- Authorization is pending near the appointment
- The patient sends records to the wrong location

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open referral record needs one owner and a next review time
- Completion requires recorded evidence that every scheduled evaluation has its clinic-defined administrative prerequisites complete or an owned exception
- Automated reminders stop after verified completion or a documented closed reason
- Keep authoritative business, customer, safety, clinical, legal, or compliance data in its approved system of record and expose only necessary coordination fields

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the PT Referral Paperwork Queue workflow concept](/products/pt-referral-paperwork-queue) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [PT Visit Plan Admin](/products/pt-visit-plan-admin).
