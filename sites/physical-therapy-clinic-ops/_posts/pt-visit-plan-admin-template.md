---
title: "Physical Therapy Visit Plan Administration Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for independent physical therapy clinics and small rehabilitation practices, with concrete fields, decision rules, and implementation steps."
productId: "pt-visit-plan-admin"
productName: "PT Visit Plan Admin"
generationFingerprint: "437054040374e25ed5dc"
date: "2026-08-30T04:38:30Z"
author:
  name: "John Smith"
---

The most useful physical therapy visit plan administration template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Visit-Plan Record identifier and source | Prevents the record from depending on memory or an inbox search | Open the visit-plan record from a verified source |
| Customer account site or operating location | Prevents the record from depending on memory or an inbox search | Collect the required inputs and operating evidence |
| Current status version and last change | Prevents the record from depending on memory or an inbox search | Validate readiness and classify material exceptions |
| Required input evidence and received time | Prevents the record from depending on memory or an inbox search | Assign the next action and communicate the decision |
| Exception category impact and decision boundary | Prevents the record from depending on memory or an inbox search | Verify the outcome and close or reschedule the visit-plan record |
| Owner next action and responsible reviewer | Prevents the record from depending on memory or an inbox search | Open the visit-plan record from a verified source |
| Due window escalation time and communication state | Prevents the record from depending on memory or an inbox search | Collect the required inputs and operating evidence |
| Verified outcome closed reason and audit note | Prevents the record from depending on memory or an inbox search | Validate readiness and classify material exceptions |

## Suggested statuses

Use workflow statuses that describe reality: **Open The Visit Plan Record From A Verified Source → Collect The Required Inputs And Operating Evidence → Validate Readiness And Classify Material Exceptions → Assign The Next Action And Communicate The Decision → Verify The Outcome And Close Or Reschedule The Visit Plan Record**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When a new visit-plan record is created or its due window changes, assign a next action and review date.
- When a required input is missing, contradictory, or no longer current, assign a next action and review date.
- When the assigned action fails, changes scope, or reaches its review time, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- A cancellation changes the last approved visit date
- A progress report is due before more visits
- Two locations count the same authorization differently

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open visit-plan record needs one owner and a next review time
- Completion requires recorded evidence that every administrative visit-plan exception has a current count, owner, and documented scheduling or payer next step
- Automated reminders stop after verified completion or a documented closed reason
- Keep authoritative business, customer, safety, clinical, legal, or compliance data in its approved system of record and expose only necessary coordination fields

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the PT Visit Plan Admin workflow concept](/products/pt-visit-plan-admin) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [PT Referral Paperwork Queue](/products/pt-referral-paperwork-queue).
