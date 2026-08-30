---
title: "Tour Departure Manifest Readiness Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for small day-tour, activity, and multi-day tour operators, with concrete fields, decision rules, and implementation steps."
productId: "departure-manifest-readiness"
productName: "Departure Manifest Readiness"
generationFingerprint: "4a28ef7a420668ca3deb"
date: "2026-08-29T21:34:11Z"
author:
  name: "John Smith"
---

The most useful tour departure manifest readiness template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Tour, departure, and capacity | Prevents the record from depending on memory or an inbox search | Create the departure roster from confirmed bookings |
| Participant and booking status | Prevents the record from depending on memory or an inbox search | Validate participant and operational requirements |
| Pickup or meeting point | Prevents the record from depending on memory or an inbox search | Assign pickup, equipment, and resource details |
| Required waiver or form status | Prevents the record from depending on memory or an inbox search | Resolve missing data and capacity exceptions |
| Equipment or size requirement | Prevents the record from depending on memory or an inbox search | Freeze, distribute, and control late manifest changes |
| Operational note and access scope | Prevents the record from depending on memory or an inbox search | Create the departure roster from confirmed bookings |
| Guide and vehicle assignment | Prevents the record from depending on memory or an inbox search | Validate participant and operational requirements |
| Manifest version, freeze time, and late change | Prevents the record from depending on memory or an inbox search | Assign pickup, equipment, and resource details |

## Suggested statuses

Use workflow statuses that describe reality: **Create The Departure Roster From Confirmed Bookings → Validate Participant And Operational Requirements → Assign Pickup Equipment And Resource Details → Resolve Missing Data And Capacity Exceptions → Freeze Distribute And Control Late Manifest Changes**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When a departure approaches its freeze time, assign a next action and review date.
- When capacity, participant status, pickup, or resource assignment changes, assign a next action and review date.
- When a blocking waiver, field, or payment state remains open, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- A kayak size is missing the night before departure
- A canceled guest still appears on a printed roster
- A pickup location changes after the guide downloads the manifest

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open departure manifest exception needs one owner and a next review time
- Completion requires recorded evidence that every departure has one frozen operational manifest with resolved blocking fields and controlled late changes
- Automated reminders stop after verified completion or a documented closed reason
- Keep the booking, capacity, manifest, guide, and resource platform as the system of record; only necessary coordination data belongs here

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Departure Manifest Readiness workflow concept](/products/departure-manifest-readiness) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Guide Cover Board](/products/guide-cover-board).
