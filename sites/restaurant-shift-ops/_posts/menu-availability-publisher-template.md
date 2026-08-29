---
title: "Restaurant 86 List And Menu Availability Tracking Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for independent restaurants and small multi-location restaurant groups, with concrete fields, decision rules, and implementation steps."
productId: "menu-availability-publisher"
productName: "Menu Availability Publisher"
generationFingerprint: "cef19eb8d1d46b337eed"
coverImage: "/assets/blog/preview/cover.jpg"
date: "2026-08-29T21:34:11Z"
author:
  name: "John Smith"
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/dynamic-routing/cover.jpg"
---

The most useful restaurant 86 list and menu availability tracking template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Location and shift | Prevents the record from depending on memory or an inbox search | Open the item availability change |
| Menu item or modifier | Prevents the record from depending on memory or an inbox search | Confirm item, modifier, location, and expected duration |
| Reason and remaining quantity | Prevents the record from depending on memory or an inbox search | Approve guest-facing wording and alternatives |
| Unavailable-from and expected return | Prevents the record from depending on memory or an inbox search | Publish across POS, online, and team channels |
| Affected channels | Prevents the record from depending on memory or an inbox search | Verify live state and schedule reactivation review |
| Approved alternative or message | Prevents the record from depending on memory or an inbox search | Open the item availability change |
| Publisher and verification evidence | Prevents the record from depending on memory or an inbox search | Confirm item, modifier, location, and expected duration |
| Reactivation owner and time | Prevents the record from depending on memory or an inbox search | Approve guest-facing wording and alternatives |

## Suggested statuses

Use workflow statuses that describe reality: **Open The Item Availability Change → Confirm Item Modifier Location And Expected Duration → Approve Guest Facing Wording And Alternatives → Publish Across Pos Online And Team Channels → Verify Live State And Schedule Reactivation Review**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When an item cannot support expected demand, assign a next action and review date.
- When one channel differs from the approved availability state, assign a next action and review date.
- When verified supply returns or the expected return time passes, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- Salmon sells out but remains on a delivery marketplace
- One sauce modifier makes two dishes unavailable
- A produce delivery arrives and the chef verifies the item can return

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open menu availability change needs one owner and a next review time
- Completion requires recorded evidence that every availability change is approved, published to all intended channels, acknowledged by service staff, and reversed only after supply is verified
- Automated reminders stop after verified completion or a documented closed reason
- Keep the POS, inventory, recipe, scheduling, and maintenance systems as the system of record; only necessary coordination data belongs here

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Menu Availability Publisher workflow concept](/products/menu-availability-publisher) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Manager Shift Handoff](/products/manager-shift-handoff).
