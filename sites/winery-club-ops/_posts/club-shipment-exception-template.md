---
title: "Wine Club Shipment Exception Tracking Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for small wineries running direct-to-consumer wine clubs and pickup programs, with concrete fields, decision rules, and implementation steps."
productId: "club-shipment-exception"
productName: "Club Shipment Exception"
generationFingerprint: "e1ae5c2d665711e4249f"
coverImage: "/assets/blog/preview/cover.jpg"
date: "2026-08-29T21:59:24Z"
author:
  name: "John Smith"
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/dynamic-routing/cover.jpg"
---

The most useful wine club shipment exception tracking template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Member club and release | Prevents the record from depending on memory or an inbox search | Open exceptions from the club release run |
| Order wines quantities and allocation | Prevents the record from depending on memory or an inbox search | Classify payment address inventory or hold cause |
| Exception type time and source | Prevents the record from depending on memory or an inbox search | Contact the member with valid resolution options |
| Payment address age and carrier state | Prevents the record from depending on memory or an inbox search | Apply the decision across DTC and fulfillment |
| Weather inventory and fulfillment hold | Prevents the record from depending on memory or an inbox search | Verify shipment cancellation pickup or carry-forward outcome |
| Member contact options response and deadline | Prevents the record from depending on memory or an inbox search | Open exceptions from the club release run |
| Order inventory and billing changes | Prevents the record from depending on memory or an inbox search | Classify payment address inventory or hold cause |
| Final tracking pickup cancellation or carry-forward | Prevents the record from depending on memory or an inbox search | Contact the member with valid resolution options |

## Suggested statuses

Use workflow statuses that describe reality: **Open Exceptions From The Club Release Run → Classify Payment Address Inventory Or Hold Cause → Contact The Member With Valid Resolution Options → Apply The Decision Across Dtc And Fulfillment → Verify Shipment Cancellation Pickup Or Carry Forward Outcome**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When a club release creates a payment address inventory or compliance hold, assign a next action and review date.
- When the member changes preference or fulfillment method, assign a next action and review date.
- When dtc carrier and fulfillment records disagree, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- A card fails during allocation
- Heat delays shipment to one region
- A pickup member requests shipping after orders are built

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open club release exception needs one owner and a next review time
- Completion requires recorded evidence that every club shipment exception reaches a member-approved or policy-based fulfillment decision with payment, inventory, carrier, and communication reconciled
- Automated reminders stop after verified completion or a documented closed reason
- Keep the winery DTC, club, POS, inventory, fulfillment, carrier, and payment platform as the system of record; only necessary coordination data belongs here

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Club Shipment Exception workflow concept](/products/club-shipment-exception) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Club Pickup Reconciliation](/products/club-pickup-reconciliation).
