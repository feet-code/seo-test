---
title: "Freight Detention Evidence Tracking: A Practical Workflow"
excerpt: "A step-by-step operating workflow for small freight brokerages and shipper-carrier coordination teams, with concrete fields, decision rules, and implementation steps."
productId: "detention-evidence-desk"
productName: "Detention Evidence Desk"
generationFingerprint: "14e2144847e351cd03f6"
coverImage: "/assets/blog/preview/cover.jpg"
date: "2026-08-29T21:34:11Z"
author:
  name: "John Smith"
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/dynamic-routing/cover.jpg"
---

Arrival and departure times, free-time terms, driver messages, location evidence, facility acknowledgments, customer approval, and carrier payment are difficult to reconcile after a load. For small freight brokerages and shipper-carrier coordination teams, the useful goal is not to add another dashboard. It is to create a small, visible process that produces this outcome: **every detention request is evaluated from agreed terms and time evidence, then reconciled across customer charge and carrier payment**.

## Define the finish line first

Write the outcome in operational terms. A teammate should be able to look at one record and tell what happened, who owns the next action, and what is blocking completion. Use these rules as the boundary:

- Every open detention request needs one owner and a next review time
- Completion requires recorded evidence that every detention request is evaluated from agreed terms and time evidence, then reconciled across customer charge and carrier payment
- Automated reminders stop after verified completion or a documented closed reason
- Keep the TMS, carrier, load, tracking, document, and billing platform as the system of record; only necessary coordination data belongs here

## A practical end-to-end workflow

### 1. Open the request against the load and stop

Record **Load, stop, facility, and parties** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can reconstruct appointment, arrival, release, and free time, or the record remains open with a reason and next action.

### 2. Reconstruct appointment, arrival, release, and free time

Record **Appointment and appointment type** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can collect facility and driver evidence, or the record remains open with a reason and next action.

### 3. Collect facility and driver evidence

Record **Arrival, check-in, dock, and release times** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can approve, revise, or deny the accessorial, or the record remains open with a reason and next action.

### 4. Approve, revise, or deny the accessorial

Record **Free-time and rate terms** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can reconcile customer billing, carrier payment, and communication, or the record remains open with a reason and next action.

### 5. Reconcile customer billing, carrier payment, and communication

Record **Tracking, BOL, or facility evidence** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can close the record and review the outcome, or the record remains open with a reason and next action.

## Handle exceptions without hiding them

The process needs an explicit waiting state. Do not mark work complete because a reminder was sent or a form was opened. Keep the record open until the real exit condition is met. These events deserve a named exception path:

- a driver reports delay beyond free time
- tracking and paperwork show different arrival or release times
- customer decision or new evidence changes the approved amount

For each exception, store the reason, the next review date, and the person who can unblock it. That makes a weekly review useful instead of turning it into a search across email, chat, and spreadsheets.

## Start with one live cycle

Run the workflow for one client, location, role, order, or participant before standardizing it. At the end, remove fields nobody used, add evidence that was missing, and keep the status list short. The workflow is ready to scale when another person can operate it without asking the original owner what each row means.

## Next step

[Explore the Detention Evidence Desk workflow concept](/products/detention-evidence-desk) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Carrier Packet Completeness](/products/carrier-packet-completeness).
