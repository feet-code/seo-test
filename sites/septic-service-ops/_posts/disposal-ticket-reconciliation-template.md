---
title: "Septic Disposal Ticket And Pump Record Reconciliation Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for small septic pumping, inspection, and liquid-waste service companies, with concrete fields, decision rules, and implementation steps."
productId: "disposal-ticket-reconciliation"
productName: "Disposal Ticket Reconciliation"
generationFingerprint: "319f2a94a04dacc4627c"
date: "2026-08-29T21:59:23Z"
author:
  name: "John Smith"
---

The most useful septic disposal ticket and pump record reconciliation template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Truck driver and load | Prevents the record from depending on memory or an inbox search | Open the load from completed pump records |
| Source jobs properties and pump records | Prevents the record from depending on memory or an inbox search | Link source jobs and measured volumes |
| Volume by job and total | Prevents the record from depending on memory or an inbox search | Record transport and disposal event |
| Departure and facility arrival times | Prevents the record from depending on memory or an inbox search | Compare accepted volume fees and evidence |
| Disposal facility and ticket number | Prevents the record from depending on memory or an inbox search | Resolve variance and release accounting |
| Accepted volume fee and ticket image | Prevents the record from depending on memory or an inbox search | Open the load from completed pump records |
| Variance reason and reviewer | Prevents the record from depending on memory or an inbox search | Link source jobs and measured volumes |
| Billing and accounting release | Prevents the record from depending on memory or an inbox search | Record transport and disposal event |

## Suggested statuses

Use workflow statuses that describe reality: **Open The Load From Completed Pump Records → Link Source Jobs And Measured Volumes → Record Transport And Disposal Event → Compare Accepted Volume Fees And Evidence → Resolve Variance And Release Accounting**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When a truck completes a disposal event, assign a next action and review date.
- When ticket volume or fee differs from linked pump records, assign a next action and review date.
- When a source job or disposal ticket remains unmatched at day close, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- Three jobs combine into one disposal load
- A facility ticket records a different unit
- A ticket photo is unreadable during billing review

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open load reconciliation needs one owner and a next review time
- Completion requires recorded evidence that every pumped load reconciles to source jobs, truck custody, accepted disposal evidence, fees, and billable service records
- Automated reminders stop after verified completion or a documented closed reason
- Keep the septic CRM, property, tank, route, pump-record, disposal, and billing platform as the system of record; only necessary coordination data belongs here

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Disposal Ticket Reconciliation workflow concept](/products/disposal-ticket-reconciliation) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Septic Site Access Readiness](/products/septic-site-access-readiness).
