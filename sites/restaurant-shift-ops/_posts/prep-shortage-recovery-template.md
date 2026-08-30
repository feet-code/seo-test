---
title: "Restaurant Prep Shortage Tracking Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for independent restaurants and small multi-location restaurant groups, with concrete fields, decision rules, and implementation steps."
productId: "prep-shortage-recovery"
productName: "Prep Shortage Recovery"
generationFingerprint: "677d447bf38ddb9c54dc"
coverImage: "/assets/blog/preview/cover.jpg"
date: "2026-08-29T21:34:11Z"
author:
  name: "John Smith"
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/dynamic-routing/cover.jpg"
---

The most useful restaurant prep shortage tracking template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Location, shift, and station | Prevents the record from depending on memory or an inbox search | Identify the shortage against the service plan |
| Prep item and unit | Prevents the record from depending on memory or an inbox search | Quantify available and required amount |
| Par, on-hand, and expected demand | Prevents the record from depending on memory or an inbox search | Choose additional prep, substitution, purchase, or menu action |
| Affected menu items | Prevents the record from depending on memory or an inbox search | Assign and execute the recovery |
| Shortage cause | Prevents the record from depending on memory or an inbox search | Verify supply and communicate the final status |
| Approved recovery action | Prevents the record from depending on memory or an inbox search | Identify the shortage against the service plan |
| Owner and ready-by time | Prevents the record from depending on memory or an inbox search | Quantify available and required amount |
| Verified quantity and communication | Prevents the record from depending on memory or an inbox search | Choose additional prep, substitution, purchase, or menu action |

## Suggested statuses

Use workflow statuses that describe reality: **Identify The Shortage Against The Service Plan → Quantify Available And Required Amount → Choose Additional Prep Substitution Purchase Or Menu Action → Assign And Execute The Recovery → Verify Supply And Communicate The Final Status**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When verified quantity falls below service demand, assign a next action and review date.
- When the recovery action misses its ready-by time, assign a next action and review date.
- When a substitution or outage changes guest-facing availability, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- Sauce yield is half the dinner par
- A delivery shortage forces an approved garnish substitute
- Additional prep will finish after the first reservation wave

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open prep shortage needs one owner and a next review time
- Completion requires recorded evidence that every service-impacting prep shortage has a quantified gap, approved response, owner, and communicated menu consequence
- Automated reminders stop after verified completion or a documented closed reason
- Keep the POS, inventory, recipe, scheduling, and maintenance systems as the system of record; only necessary coordination data belongs here

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Prep Shortage Recovery workflow concept](/products/prep-shortage-recovery) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Menu Availability Publisher](/products/menu-availability-publisher).
