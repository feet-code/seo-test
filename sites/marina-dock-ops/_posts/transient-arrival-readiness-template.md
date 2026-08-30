---
title: "Marina Transient Arrival Readiness Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for independent marinas, yacht clubs, and small dock operations, with concrete fields, decision rules, and implementation steps."
productId: "transient-arrival-readiness"
productName: "Transient Arrival Readiness"
generationFingerprint: "68a6a5083bc5a3ee0c77"
date: "2026-08-29T21:34:11Z"
author:
  name: "John Smith"
---

The most useful marina transient arrival readiness template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Marina, reservation, and boater | Prevents the record from depending on memory or an inbox search | Create readiness from the confirmed reservation |
| Vessel length, beam, draft, and power | Prevents the record from depending on memory or an inbox search | Validate vessel, dates, services, and contact details |
| Arrival and departure window | Prevents the record from depending on memory or an inbox search | Assign a compatible available slip |
| Assigned slip and compatibility checks | Prevents the record from depending on memory or an inbox search | Confirm access, utilities, arrival, and payment instructions |
| Utility and service requests | Prevents the record from depending on memory or an inbox search | Release the arrival plan to boater and dock team |
| Balance and payment plan | Prevents the record from depending on memory or an inbox search | Create readiness from the confirmed reservation |
| Access and contact instructions | Prevents the record from depending on memory or an inbox search | Validate vessel, dates, services, and contact details |
| Dockhand owner and acknowledgment | Prevents the record from depending on memory or an inbox search | Assign a compatible available slip |

## Suggested statuses

Use workflow statuses that describe reality: **Create Readiness From The Confirmed Reservation → Validate Vessel Dates Services And Contact Details → Assign A Compatible Available Slip → Confirm Access Utilities Arrival And Payment Instructions → Release The Arrival Plan To Boater And Dock Team**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When a transient reservation is confirmed, assign a next action and review date.
- When vessel, timing, service, or slip availability changes, assign a next action and review date.
- When a readiness field remains open near the arrival window, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- A sailboat draft conflicts with the assigned slip
- A late arrival needs after-hours gate instructions
- Shore-power needs change after the dock team receives the plan

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every open transient slip arrival needs one owner and a next review time
- Completion requires recorded evidence that every transient arrival has a compatible assigned slip, current instructions, payment plan, and acknowledged dock handoff
- Automated reminders stop after verified completion or a documented closed reason
- Keep the slip, reservation, boater, billing, utility, and maintenance platform as the system of record; only necessary coordination data belongs here

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Transient Arrival Readiness workflow concept](/products/transient-arrival-readiness) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Dock Maintenance Handoff](/products/dock-maintenance-handoff).
