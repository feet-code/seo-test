---
title: "Tour Guide Scheduling And Substitution: A Practical Workflow"
excerpt: "A step-by-step operating workflow for small day-tour, activity, and multi-day tour operators, with concrete fields, decision rules, and implementation steps."
productId: "guide-cover-board"
productName: "Guide Cover Board"
generationFingerprint: "0fa8921991b544dcfe7d"
date: "2026-08-29T21:34:11Z"
author:
  name: "John Smith"
---

Guide callouts are solved through group messages without consistently checking qualification, language, availability, transport, pay, and manifest acceptance. For small day-tour, activity, and multi-day tour operators, the useful goal is not to add another dashboard. It is to create a small, visible process that produces this outcome: **every uncovered departure is accepted by a qualified guide or escalated to a documented operating decision before the guest notice cutoff**.

## Define the finish line first

Write the outcome in operational terms. A teammate should be able to look at one record and tell what happened, who owns the next action, and what is blocking completion. Use these rules as the boundary:

- Every open guide coverage exception needs one owner and a next review time
- Completion requires recorded evidence that every uncovered departure is accepted by a qualified guide or escalated to a documented operating decision before the guest notice cutoff
- Automated reminders stop after verified completion or a documented closed reason
- Keep the booking, capacity, manifest, guide, and resource platform as the system of record; only necessary coordination data belongs here

## A practical end-to-end workflow

### 1. Open the coverage exception against the departure

Record **Tour, departure, and meeting point** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can identify qualified and available guides, or the record remains open with a reason and next action.

### 2. Identify qualified and available guides

Record **Original guide and exception** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can offer and confirm the assignment, or the record remains open with a reason and next action.

### 3. Offer and confirm the assignment

Record **Required qualification and language** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can transfer manifest, access, and resource instructions, or the record remains open with a reason and next action.

### 4. Transfer manifest, access, and resource instructions

Record **Available candidate guides** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can verify guide acceptance and publish the operating plan, or the record remains open with a reason and next action.

### 5. Verify guide acceptance and publish the operating plan

Record **Confirmed guide and acceptance time** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can close the record and review the outcome, or the record remains open with a reason and next action.

## Handle exceptions without hiding them

The process needs an explicit waiting state. Do not mark work complete because a reminder was sent or a form was opened. Keep the record open until the real exit condition is met. These events deserve a named exception path:

- an assigned guide becomes unavailable
- no qualified guide accepts by the escalation time
- the replacement cannot access the current manifest or resources

For each exception, store the reason, the next review date, and the person who can unblock it. That makes a weekly review useful instead of turning it into a search across email, chat, and spreadsheets.

## Start with one live cycle

Run the workflow for one client, location, role, order, or participant before standardizing it. At the end, remove fields nobody used, add evidence that was missing, and keep the status list short. The workflow is ready to scale when another person can operate it without asking the original owner what each row means.

## Next step

[Explore the Guide Cover Board workflow concept](/products/guide-cover-board) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Departure Manifest Readiness](/products/departure-manifest-readiness).
