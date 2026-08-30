---
title: "Moving Inventory Change Authorization Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for independent household moving companies and local moving crews, with concrete fields, decision rules, and implementation steps."
productId: "move-inventory-change-register"
productName: "Move Inventory Change Register"
generationFingerprint: "8d6790b87cc8fb8ffe73"
coverImage: "/assets/blog/preview/cover.jpg"
date: "2026-08-29T21:34:11Z"
author:
  name: "John Smith"
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/dynamic-routing/cover.jpg"
---

The most useful moving inventory change authorization template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Customer, move, and estimate | Prevents the record from depending on memory or an inbox search | Log the requested or observed scope change |
| Original and changed inventory | Prevents the record from depending on memory or an inbox search | Compare it with the approved estimate and inventory |
| Change source and time | Prevents the record from depending on memory or an inbox search | Assess labor, equipment, timing, and price impact |
| Origin or destination access change | Prevents the record from depending on memory or an inbox search | Obtain customer and operations authorization |
| Labor, vehicle, equipment, and date impact | Prevents the record from depending on memory or an inbox search | Publish the effective scope and preserve the prior version |
| Price and valuation impact | Prevents the record from depending on memory or an inbox search | Log the requested or observed scope change |
| Customer and operations approval | Prevents the record from depending on memory or an inbox search | Compare it with the approved estimate and inventory |
| Effective version and crew acknowledgment | Prevents the record from depending on memory or an inbox search | Assess labor, equipment, timing, and price impact |

## Suggested statuses

Use workflow statuses that describe reality: **Log The Requested Or Observed Scope Change → Compare It With The Approved Estimate And Inventory → Assess Labor Equipment Timing And Price Impact → Obtain Customer And Operations Authorization → Publish The Effective Scope And Preserve The Prior Version**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When the customer adds or removes inventory, assign a next action and review date.
- When crew observes access or packing work outside the estimate, assign a next action and review date.
- When date, address, vehicle, or labor requirements change, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- A customer adds a garage after the estimate
- A long carry is discovered at destination
- An elevator window forces a different crew start

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open move scope change needs one owner and a next review time
- Completion requires recorded evidence that every material move change is priced, authorized, and published to dispatch and crew before the affected work proceeds
- Automated reminders stop after verified completion or a documented closed reason
- Keep the estimate, bill-of-lading, dispatch, inventory, and claims system as the system of record; only necessary coordination data belongs here

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Move Inventory Change Register workflow concept](/products/move-inventory-change-register) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Crew Arrival Readiness](/products/crew-arrival-readiness).
