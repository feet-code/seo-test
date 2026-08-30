---
title: "Salon And Spa Room Inventory Par Tracking Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for independent salons, spas, and small wellness studios, with concrete fields, decision rules, and implementation steps."
productId: "service-room-par-tracker"
productName: "Service Room Par Tracker"
generationFingerprint: "485ef056754c91568324"
date: "2026-08-29T21:05:26Z"
author:
  name: "John Smith"
---

The most useful salon and spa room inventory par tracking template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Location and service room | Prevents the record from depending on memory or an inbox search | Set par levels by room and service |
| Supply item and unit | Prevents the record from depending on memory or an inbox search | Record the room count at the operating cadence |
| Par and reorder threshold | Prevents the record from depending on memory or an inbox search | Create replenishment work for shortages |
| Counted quantity and time | Prevents the record from depending on memory or an inbox search | Resolve stockout, transfer, or count variance |
| Upcoming service demand | Prevents the record from depending on memory or an inbox search | Confirm the room is ready and update central stock |
| Replenishment quantity | Prevents the record from depending on memory or an inbox search | Set par levels by room and service |
| Owner and source location | Prevents the record from depending on memory or an inbox search | Record the room count at the operating cadence |
| Completion or variance evidence | Prevents the record from depending on memory or an inbox search | Create replenishment work for shortages |

## Suggested statuses

Use workflow statuses that describe reality: **Set Par Levels By Room And Service → Record The Room Count At The Operating Cadence → Create Replenishment Work For Shortages → Resolve Stockout Transfer Or Count Variance → Confirm The Room Is Ready And Update Central Stock**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When a count falls below par before a booked service, assign a next action and review date.
- When central stock cannot fulfill the replenishment quantity, assign a next action and review date.
- When verified usage differs materially from expected usage, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- A facial room has one mask left before a fully booked afternoon
- Wax is moved between rooms but central stock is not updated
- Glove usage rises after a new service protocol

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open service-room replenishment task needs one owner and a next review time
- Completion requires recorded evidence that each service room is replenished to an agreed par before its next booked service without hiding inventory variance
- Automated reminders stop after verified completion or a documented closed reason
- Keep booking and point-of-sale platform as the system of record; only necessary coordination data belongs here

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Service Room Par Tracker workflow concept](/products/service-room-par-tracker) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Rebooking Recovery List](/products/rebooking-recovery-list).
