---
title: "Dumpster Contamination And Overage Evidence Tracking Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for small roll-off dumpster and commercial waste-container rental companies, with concrete fields, decision rules, and implementation steps."
productId: "overage-evidence-desk"
productName: "Overage Evidence Desk"
generationFingerprint: "7c8f858b3aab30c3176d"
coverImage: "/assets/blog/preview/cover.jpg"
date: "2026-08-29T21:59:23Z"
author:
  name: "John Smith"
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/dynamic-routing/cover.jpg"
---

The most useful dumpster contamination and overage evidence tracking template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Customer order site and container | Prevents the record from depending on memory or an inbox search | Open the exception from driver or scale evidence |
| Exception type and detected time | Prevents the record from depending on memory or an inbox search | Match it to order and contract rule |
| Contract rule price and threshold | Prevents the record from depending on memory or an inbox search | Validate amount photos ticket and timing |
| Driver photos notes and location | Prevents the record from depending on memory or an inbox search | Review charge waive or correction decision |
| Scale ticket weight and facility | Prevents the record from depending on memory or an inbox search | Notify the customer and release billing |
| Calculation tax and proposed charge | Prevents the record from depending on memory or an inbox search | Open the exception from driver or scale evidence |
| Reviewer decision and rationale | Prevents the record from depending on memory or an inbox search | Match it to order and contract rule |
| Customer notice dispute and invoice status | Prevents the record from depending on memory or an inbox search | Validate amount photos ticket and timing |

## Suggested statuses

Use workflow statuses that describe reality: **Open The Exception From Driver Or Scale Evidence → Match It To Order And Contract Rule → Validate Amount Photos Ticket And Timing → Review Charge Waive Or Correction Decision → Notify The Customer And Release Billing**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When a driver or facility identifies a billable exception, assign a next action and review date.
- When required evidence or contract rule is missing, assign a next action and review date.
- When the customer disputes the proposed charge, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- A load exceeds included tonnage
- Mattresses appear in a prohibited-material load
- A pickup is blocked by a parked vehicle

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open exception charge needs one owner and a next review time
- Completion requires recorded evidence that every exception charge is linked to the contract rule, timestamped field or scale evidence, reviewer decision, and customer notice before invoicing
- Automated reminders stop after verified completion or a documented closed reason
- Keep the waste CRM, contract, dispatch, driver, scale-ticket, container, and billing platform as the system of record; only necessary coordination data belongs here

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Overage Evidence Desk workflow concept](/products/overage-evidence-desk) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Container Inventory Reconciliation](/products/container-inventory-reconciliation).
