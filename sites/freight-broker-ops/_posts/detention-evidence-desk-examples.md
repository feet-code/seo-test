---
title: "Freight Detention Evidence Tracking Examples: Three Workflow Scenarios"
excerpt: "Three realistic workflow test cases for small freight brokerages and shipper-carrier coordination teams, with concrete fields, decision rules, and implementation steps."
productId: "detention-evidence-desk"
productName: "Detention Evidence Desk"
generationFingerprint: "14e2144847e351cd03f6"
date: "2026-08-29T21:34:11Z"
author:
  name: "John Smith"
---

Examples make freight detention evidence tracking easier to design because they reveal where a neat diagram meets messy work. The scenarios below are not claims about a particular company; they are test cases small freight brokerages and shipper-carrier coordination teams can run against a template or software trial.

### Scenario 1: Geofence arrival precedes facility check-in by twenty minutes

Create the record before the first follow-up. Capture Load, stop, facility, and parties, Appointment and appointment type, Arrival, check-in, dock, and release times, then move it through open the request against the load and stop and reconstruct appointment, arrival, release, and free time. If a driver reports delay beyond free time, do not improvise in a private message; assign the exception, set a review date, and preserve the evidence needed for the next decision. Close with an explicit outcome and reason. ### Scenario 2: A BOL has no release time

Create the record before the first follow-up. Capture Appointment and appointment type, Arrival, check-in, dock, and release times, Free-time and rate terms, then move it through open the request against the load and stop and reconstruct appointment, arrival, release, and free time. If tracking and paperwork show different arrival or release times, do not improvise in a private message; assign the exception, set a review date, and preserve the evidence needed for the next decision. Close with an explicit outcome and reason. ### Scenario 3: The customer approves two hours while the carrier requests three

Create the record before the first follow-up. Capture Arrival, check-in, dock, and release times, Free-time and rate terms, Tracking, BOL, or facility evidence, then move it through open the request against the load and stop and reconstruct appointment, arrival, release, and free time. If customer decision or new evidence changes the approved amount, do not improvise in a private message; assign the exception, set a review date, and preserve the evidence needed for the next decision. Close with an explicit outcome and reason.

## Debrief each scenario

After running a scenario, ask:

- Did the record make every open detention request needs one owner and a next review time?
- Did the record make completion requires recorded evidence that every detention request is evaluated from agreed terms and time evidence, then reconciled across customer charge and carrier payment?
- Did the record make automated reminders stop after verified completion or a documented closed reason?
- Did the record make keep the tms, carrier, load, tracking, document, and billing platform as the system of record; only necessary coordination data belongs here?

Also check whether a new teammate could identify the owner, next action, and finish condition without opening another system.

## Convert scenarios into acceptance tests

Use the normal case, waiting case, and closed-without-completion case in every software demo. Require the vendor—or your own prototype—to show the full workflow rather than isolated feature screens. Export the resulting records and verify that the status history remains understandable.

## Next step

[Explore the Detention Evidence Desk workflow concept](/products/detention-evidence-desk) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Carrier Packet Completeness](/products/carrier-packet-completeness).
