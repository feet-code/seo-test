---
title: "Freight Detention Evidence Tracking Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for small freight brokerages and shipper-carrier coordination teams, with concrete fields, decision rules, and implementation steps."
productId: "detention-evidence-desk"
productName: "Detention Evidence Desk"
generationFingerprint: "14e2144847e351cd03f6"
date: "2026-08-29T21:34:11Z"
author:
  name: "John Smith"
---

The most useful freight detention evidence tracking template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Load, stop, facility, and parties | Prevents the record from depending on memory or an inbox search | Open the request against the load and stop |
| Appointment and appointment type | Prevents the record from depending on memory or an inbox search | Reconstruct appointment, arrival, release, and free time |
| Arrival, check-in, dock, and release times | Prevents the record from depending on memory or an inbox search | Collect facility and driver evidence |
| Free-time and rate terms | Prevents the record from depending on memory or an inbox search | Approve, revise, or deny the accessorial |
| Tracking, BOL, or facility evidence | Prevents the record from depending on memory or an inbox search | Reconcile customer billing, carrier payment, and communication |
| Delay cause and exception | Prevents the record from depending on memory or an inbox search | Open the request against the load and stop |
| Customer decision and amount | Prevents the record from depending on memory or an inbox search | Reconstruct appointment, arrival, release, and free time |
| Carrier payment and billing reconciliation | Prevents the record from depending on memory or an inbox search | Collect facility and driver evidence |

## Suggested statuses

Use workflow statuses that describe reality: **Open The Request Against The Load And Stop → Reconstruct Appointment Arrival Release And Free Time → Collect Facility And Driver Evidence → Approve Revise Or Deny The Accessorial → Reconcile Customer Billing Carrier Payment And Communication**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When a driver reports delay beyond free time, assign a next action and review date.
- When tracking and paperwork show different arrival or release times, assign a next action and review date.
- When customer decision or new evidence changes the approved amount, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- Geofence arrival precedes facility check-in by twenty minutes
- A BOL has no release time
- The customer approves two hours while the carrier requests three

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open detention request needs one owner and a next review time
- Completion requires recorded evidence that every detention request is evaluated from agreed terms and time evidence, then reconciled across customer charge and carrier payment
- Automated reminders stop after verified completion or a documented closed reason
- Keep the TMS, carrier, load, tracking, document, and billing platform as the system of record; only necessary coordination data belongs here

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Detention Evidence Desk workflow concept](/products/detention-evidence-desk) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Carrier Packet Completeness](/products/carrier-packet-completeness).
