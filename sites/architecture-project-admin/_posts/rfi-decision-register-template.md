---
title: "Architectural Rfi Decision Tracking Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for small architecture firms and design-project administrators, with concrete fields, decision rules, and implementation steps."
productId: "rfi-decision-register"
productName: "RFI Decision Register"
generationFingerprint: "47b7db28daa17a0bd8ea"
date: "2026-08-29T21:05:26Z"
author:
  name: "John Smith"
---

The most useful architectural RFI decision tracking template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Project and RFI number | Prevents the record from depending on memory or an inbox search | Register the question and governing references |
| Question and location | Prevents the record from depending on memory or an inbox search | Assign the decision owner and needed-by date |
| Referenced drawing or specification | Prevents the record from depending on memory or an inbox search | Develop and approve the response |
| Originator and responsible party | Prevents the record from depending on memory or an inbox search | Assess cost, schedule, and document impact |
| Needed-by date | Prevents the record from depending on memory or an inbox search | Distribute the decision and verify follow-through |
| Approved response and attachments | Prevents the record from depending on memory or an inbox search | Register the question and governing references |
| Cost, schedule, and scope impact | Prevents the record from depending on memory or an inbox search | Assign the decision owner and needed-by date |
| Distribution and document-update evidence | Prevents the record from depending on memory or an inbox search | Develop and approve the response |

## Suggested statuses

Use workflow statuses that describe reality: **Register The Question And Governing References → Assign The Decision Owner And Needed By Date → Develop And Approve The Response → Assess Cost Schedule And Document Impact → Distribute The Decision And Verify Follow Through**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When an rfi approaches its needed-by date without a decision, assign a next action and review date.
- When the response changes cost, schedule, scope, or controlled documents, assign a next action and review date.
- When field conditions or a revision supersede the published response, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- A ceiling conflict needs a sketch before framing continues
- A response selects a product but the specification remains unchanged
- A field clarification is later superseded by an issued bulletin

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open RFI decision needs one owner and a next review time
- Completion requires recorded evidence that every RFI response identifies the authoritative decision, impact, and required document updates before operational closure
- Automated reminders stop after verified completion or a documented closed reason
- Keep controlled drawing, specification, RFI, and submittal repository as the system of record; only necessary coordination data belongs here

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the RFI Decision Register workflow concept](/products/rfi-decision-register) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Consultant Deliverable Board](/products/consultant-deliverable-board).
