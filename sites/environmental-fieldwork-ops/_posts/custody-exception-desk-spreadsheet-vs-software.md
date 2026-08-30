---
title: "Custody Exception Desk vs. a Spreadsheet: When Software Is Worth It"
excerpt: "A spreadsheet-versus-software decision guide for small environmental consulting and field-sampling teams, with concrete fields, decision rules, and implementation steps."
productId: "custody-exception-desk"
productName: "Custody Exception Desk"
generationFingerprint: "0c01731d2898bf890584"
date: "2026-08-29T21:59:24Z"
author:
  name: "John Smith"
---

A spreadsheet is often the right first implementation for environmental chain of custody exception tracking. It is cheap, editable, and forces the team to define the workflow. The question is not whether spreadsheets are good or bad; it is when coordination costs become larger than the flexibility is worth.

## Compare the realistic options

| Approach | Best when | Main limitation |
|---|---|---|
| Sampling plans, cooler checklists, paper custody forms, field books, and lab emails | One owner handles low volume and can see every open item | Status and follow-up history depend on memory and inbox searches |
| Environmental data software or a shared field-to-lab exception board | The team already maintains it and exceptions are simple | Purpose-built reminders, evidence, and stop conditions require manual setup |
| A focused workflow tool | The same coordination failure repeats across many live records | It must integrate with the system of record and justify another workflow |

## A spreadsheet is still enough when

- One owner can reliably manage register the discrepancy at transfer or receipt.
- One owner can reliably manage contain and identify affected samples.
- One owner can reliably manage compare original field transfer and laboratory evidence.

It also remains a good fit when volume is low, exceptions are rare, and the team reviews the sheet at a fixed cadence.

## Signals that a focused tool may be justified

- field or laboratory staff detects a custody mismatch
- hold time or sample condition makes review urgent
- clarification changes laboratory acceptance or reporting status

The strongest signal is repeated coordination work: copying status between systems, rebuilding the same reminders, or asking people for information that should already be attached to the record.

## Run a switching-cost test

Before migrating, recreate ten current records using the candidate tool. Confirm that it supports these fields without awkward workarounds: Project event shipment and cooler, Sample IDs containers and requested analyses, Collector transfer receiver and timestamps, Seal condition temperature and preservation, Original custody form and label images, Discrepancy type affected samples and impact, Qualified reviewer disposition and rationale, Laboratory status correction link and notification. Then walk one exception from start to finish. Test exports and deletion before importing the full history.

Also test permissions with a real role boundary. The person doing the work, the reviewer, and an external client or participant should not automatically see the same information. Export a sample record and confirm that its status history, attachments, and ownership remain understandable outside the vendor interface.

## Avoid the all-in-one trap

A broad platform can be valuable when workflows genuinely share data. It can also force a small team to configure modules it does not need. Compare the time required to operate the system, not the number of features on the pricing page.

## Next step

[Explore the Custody Exception Desk workflow concept](/products/custody-exception-desk) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Sampling Event Readiness](/products/sampling-event-readiness).
