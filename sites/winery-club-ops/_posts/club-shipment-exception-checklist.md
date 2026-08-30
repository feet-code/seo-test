---
title: "Wine Club Shipment Exception Tracking Checklist for Small Wineries Running Direct-To-Consumer Wine Clubs And Pickup Programs"
excerpt: "A copyable quality-control checklist for small wineries running direct-to-consumer wine clubs and pickup programs, with concrete fields, decision rules, and implementation steps."
productId: "club-shipment-exception"
productName: "Club Shipment Exception"
generationFingerprint: "e1ae5c2d665711e4249f"
date: "2026-08-29T21:59:24Z"
author:
  name: "John Smith"
---

A checklist for wine club shipment exception tracking should prevent missing decisions, not merely prove that somebody clicked boxes. The checklist below is designed for small wineries running direct-to-consumer wine clubs and pickup programs and centers on one result: **every club shipment exception reaches a member-approved or policy-based fulfillment decision with payment, inventory, carrier, and communication reconciled**.

## Before the work starts

- Confirm Member club and release
- Confirm Order wines quantities and allocation
- Confirm Exception type time and source
- Confirm Payment address age and carrier state

Also name the owner and the expected completion condition. If either is unknown, the work is not ready to enter the active queue.

## While the work is moving

- Update Open exceptions from the club release run
- Update Classify payment address inventory or hold cause
- Update Contact the member with valid resolution options
- Update Apply the decision across DTC and fulfillment
- Update Verify shipment cancellation pickup or carry-forward outcome

Every update should change a decision. Notes such as “followed up” are weak unless they also include the channel, result, next date, and owner.

## Before marking it complete

- Verify Weather inventory and fulfillment hold
- Verify Member contact options response and deadline
- Verify Order inventory and billing changes
- Verify Final tracking pickup cancellation or carry-forward

Confirm that the actual outcome—not just an activity—has been recorded. If the process ended early, use a closed reason rather than deleting the record.

## Copy-and-paste weekly review

- [ ] Review records where a club release creates a payment address inventory or compliance hold
- [ ] Review records where the member changes preference or fulfillment method
- [ ] Review records where dtc carrier and fulfillment records disagree

- [ ] Check for retrying cards without respecting communication policy
- [ ] Check for changing wine allocation without member or club-rule basis
- [ ] Check for releasing fulfillment while an address hold remains
- [ ] Check for closing when the dtc order updates but warehouse status does not

## Make the checklist measurable

Choose one metric before the next cycle. Good options for this workflow are Exception resolution rate, Cross-system correction rate, Recovered-order rate. A checklist that never changes a metric or prevents a known failure mode is probably administrative overhead.

## Assign ownership and escalation

Put one role—not a group—next to every item that can remain open. Define a backup owner and an escalation time for work that affects a customer, client, participant, or delivery promise. During review, separate **not started**, **waiting on someone**, and **failed validation**; those states need different actions. If a checklist item repeatedly waits on the same dependency, redesign the intake or handoff instead of adding more reminder boxes.

## Next step

[Explore the Club Shipment Exception workflow concept](/products/club-shipment-exception) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Club Pickup Reconciliation](/products/club-pickup-reconciliation).
