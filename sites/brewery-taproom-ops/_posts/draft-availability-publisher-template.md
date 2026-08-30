---
title: "Brewery Tap List Availability Tracking Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for independent craft breweries operating one or more taprooms, with concrete fields, decision rules, and implementation steps."
productId: "draft-availability-publisher"
productName: "Draft Availability Publisher"
generationFingerprint: "01e68dbb40ae388a4d92"
date: "2026-08-29T21:59:24Z"
author:
  name: "John Smith"
---

The most useful brewery tap list availability tracking template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Taproom line beer and batch | Prevents the record from depending on memory or an inbox search | Open the beer and line availability change |
| Change reason time and reporter | Prevents the record from depending on memory or an inbox search | Confirm inventory hold and expected duration |
| Keg quantity inventory and hold state | Prevents the record from depending on memory or an inbox search | Approve replacement wording and sales behavior |
| Expected return and replacement option | Prevents the record from depending on memory or an inbox search | Publish across POS boards web and staff |
| Affected POS board web and menu channels | Prevents the record from depending on memory or an inbox search | Verify live state and schedule reactivation review |
| Approver publisher and staff notice | Prevents the record from depending on memory or an inbox search | Open the beer and line availability change |
| Live verification evidence | Prevents the record from depending on memory or an inbox search | Confirm inventory hold and expected duration |
| Reactivation owner condition and time | Prevents the record from depending on memory or an inbox search | Approve replacement wording and sales behavior |

## Suggested statuses

Use workflow statuses that describe reality: **Open The Beer And Line Availability Change → Confirm Inventory Hold And Expected Duration → Approve Replacement Wording And Sales Behavior → Publish Across Pos Boards Web And Staff → Verify Live State And Schedule Reactivation Review**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When a keg kicks or beer is held, assign a next action and review date.
- When one guest-facing channel differs from approved state, assign a next action and review date.
- When verified keg and line readiness supports reactivation, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- A seasonal keg kicks during dinner
- One batch is placed on quality hold
- A replacement keg arrives but the line is not cleaned

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open draft availability change needs one owner and a next review time
- Completion requires recorded evidence that every draft availability change is approved, published across intended channels, verified live, and reactivated only from confirmed product and line readiness
- Automated reminders stop after verified completion or a documented closed reason
- Keep the brewery production, keg inventory, taproom POS, event, staff, and maintenance platform as the system of record; only necessary coordination data belongs here

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Draft Availability Publisher workflow concept](/products/draft-availability-publisher) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Taproom Event Shift Handoff](/products/taproom-event-shift-handoff).
