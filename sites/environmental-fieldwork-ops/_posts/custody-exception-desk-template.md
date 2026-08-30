---
title: "Environmental Chain Of Custody Exception Tracking Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for small environmental consulting and field-sampling teams, with concrete fields, decision rules, and implementation steps."
productId: "custody-exception-desk"
productName: "Custody Exception Desk"
generationFingerprint: "0c01731d2898bf890584"
date: "2026-08-29T21:59:24Z"
author:
  name: "John Smith"
---

The most useful environmental chain of custody exception tracking template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Project event shipment and cooler | Prevents the record from depending on memory or an inbox search | Register the discrepancy at transfer or receipt |
| Sample IDs containers and requested analyses | Prevents the record from depending on memory or an inbox search | Contain and identify affected samples |
| Collector transfer receiver and timestamps | Prevents the record from depending on memory or an inbox search | Compare original field transfer and laboratory evidence |
| Seal condition temperature and preservation | Prevents the record from depending on memory or an inbox search | Obtain qualified disposition or clarification |
| Original custody form and label images | Prevents the record from depending on memory or an inbox search | Preserve correction linkage and final sample status |
| Discrepancy type affected samples and impact | Prevents the record from depending on memory or an inbox search | Register the discrepancy at transfer or receipt |
| Qualified reviewer disposition and rationale | Prevents the record from depending on memory or an inbox search | Contain and identify affected samples |
| Laboratory status correction link and notification | Prevents the record from depending on memory or an inbox search | Compare original field transfer and laboratory evidence |

## Suggested statuses

Use workflow statuses that describe reality: **Register The Discrepancy At Transfer Or Receipt → Contain And Identify Affected Samples → Compare Original Field Transfer And Laboratory Evidence → Obtain Qualified Disposition Or Clarification → Preserve Correction Linkage And Final Sample Status**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When field or laboratory staff detects a custody mismatch, assign a next action and review date.
- When hold time or sample condition makes review urgent, assign a next action and review date.
- When clarification changes laboratory acceptance or reporting status, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- A cooler arrives with one fewer container than the form
- A transfer signature lacks a time
- A label ID differs by one character from the custody record

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open sample custody exception needs one owner and a next review time
- Completion requires recorded evidence that every custody discrepancy is contained, reviewed by qualified personnel, linked to affected samples, and resolved without rewriting original evidence
- Automated reminders stop after verified completion or a documented closed reason
- Keep the environmental project, sampling plan, field form, sample, laboratory, and reporting platform as the system of record; only necessary coordination data belongs here

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Custody Exception Desk workflow concept](/products/custody-exception-desk) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Sampling Event Readiness](/products/sampling-event-readiness).
