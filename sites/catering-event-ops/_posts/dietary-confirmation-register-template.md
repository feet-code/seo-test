---
title: "Catering Dietary And Allergen Confirmation Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for independent caterers and small event-food teams, with concrete fields, decision rules, and implementation steps."
productId: "dietary-confirmation-register"
productName: "Dietary Confirmation Register"
generationFingerprint: "f301d76191c691b289d9"
coverImage: "/assets/blog/preview/cover.jpg"
date: "2026-08-29T21:05:26Z"
author:
  name: "John Smith"
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/dynamic-routing/cover.jpg"
---

The most useful catering dietary and allergen confirmation template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Event and guest identifier | Prevents the record from depending on memory or an inbox search | Capture the request and original wording |
| Original request and source | Prevents the record from depending on memory or an inbox search | Clarify guest, severity context, and contact path |
| Dietary or allergen category | Prevents the record from depending on memory or an inbox search | Review menu feasibility with authorized staff |
| Clarification status and contact | Prevents the record from depending on memory or an inbox search | Approve preparation and service controls |
| Affected menu items | Prevents the record from depending on memory or an inbox search | Publish the final register and confirm late exceptions |
| Approved accommodation or limitation | Prevents the record from depending on memory or an inbox search | Capture the request and original wording |
| Kitchen and service owners | Prevents the record from depending on memory or an inbox search | Clarify guest, severity context, and contact path |
| Confirmation time and final event-order version | Prevents the record from depending on memory or an inbox search | Review menu feasibility with authorized staff |

## Suggested statuses

Use workflow statuses that describe reality: **Capture The Request And Original Wording → Clarify Guest Severity Context And Contact Path → Review Menu Feasibility With Authorized Staff → Approve Preparation And Service Controls → Publish The Final Register And Confirm Late Exceptions**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When a request is ambiguous or missing a guest count, assign a next action and review date.
- When the requested accommodation conflicts with menu or facility controls, assign a next action and review date.
- When a new requirement arrives after the production cutoff, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- The planner lists GF without identifying which guests
- A severe allergy request needs a direct feasibility conversation
- A late guest update changes two plated meals after prep sheets print

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open dietary requirement needs one owner and a next review time
- Completion requires recorded evidence that every declared dietary or allergen requirement is clarified, approved into the event plan, and communicated to production and service owners
- Automated reminders stop after verified completion or a documented closed reason
- Keep signed event order, recipe, allergen, and production systems as the system of record; only necessary coordination data belongs here

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Dietary Confirmation Register workflow concept](/products/dietary-confirmation-register) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Event Change Cutoff Log](/products/event-change-cutoff-log).
