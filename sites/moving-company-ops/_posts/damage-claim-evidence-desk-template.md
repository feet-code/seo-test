---
title: "Moving Company Damage Claim Evidence Tracking Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for independent household moving companies and local moving crews, with concrete fields, decision rules, and implementation steps."
productId: "damage-claim-evidence-desk"
productName: "Damage Claim Evidence Desk"
generationFingerprint: "8a8b969b87f75615775a"
coverImage: "/assets/blog/preview/cover.jpg"
date: "2026-08-29T21:34:11Z"
author:
  name: "John Smith"
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/dynamic-routing/cover.jpg"
---

The most useful moving company damage claim evidence tracking template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Customer, shipment, and bill of lading | Prevents the record from depending on memory or an inbox search | Register the written claim and shipment |
| Claim received date and deadline | Prevents the record from depending on memory or an inbox search | Itemize loss or damage against inventory |
| Item and inventory number | Prevents the record from depending on memory or an inbox search | Collect photos, value, and repair evidence |
| Damage or loss description | Prevents the record from depending on memory or an inbox search | Review responsibility and authorized remedy |
| Pickup, delivery, and claim photos | Prevents the record from depending on memory or an inbox search | Communicate the decision and record settlement or closure |
| Value, repair estimate, and valuation terms | Prevents the record from depending on memory or an inbox search | Register the written claim and shipment |
| Reviewer and decision rationale | Prevents the record from depending on memory or an inbox search | Itemize loss or damage against inventory |
| Offer, settlement, denial, or follow-up | Prevents the record from depending on memory or an inbox search | Collect photos, value, and repair evidence |

## Suggested statuses

Use workflow statuses that describe reality: **Register The Written Claim And Shipment → Itemize Loss Or Damage Against Inventory → Collect Photos Value And Repair Evidence → Review Responsibility And Authorized Remedy → Communicate The Decision And Record Settlement Or Closure**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When a written loss or damage claim arrives, assign a next action and review date.
- When required item, shipment, photo, or value evidence is missing, assign a next action and review date.
- When inspection, estimate, or customer response changes the proposed remedy, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- A dresser scratch is tied to one inventory tag
- A missing carton claim lacks delivery inventory evidence
- A repair estimate arrives after the initial claim submission

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open moving damage claim needs one owner and a next review time
- Completion requires recorded evidence that every damage or loss claim is acknowledged, completed with required evidence, reviewed, and resolved with a documented decision
- Automated reminders stop after verified completion or a documented closed reason
- Keep the estimate, bill-of-lading, dispatch, inventory, and claims system as the system of record; only necessary coordination data belongs here

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Damage Claim Evidence Desk workflow concept](/products/damage-claim-evidence-desk) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Move Inventory Change Register](/products/move-inventory-change-register).
