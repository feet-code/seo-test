---
title: "Csa Skip Swap And Pickup Change Tracking: A Practical Workflow"
excerpt: "A step-by-step operating workflow for small community-supported agriculture farms and farm-box programs, with concrete fields, decision rules, and implementation steps."
productId: "member-change-cutoff"
productName: "Member Change Cutoff"
generationFingerprint: "f44afdbf2a92d0b6b942"
date: "2026-08-29T21:05:26Z"
author:
  name: "John Smith"
---

Skips, pickup moves, box swaps, donations, vacation holds, and address changes arrive around harvest and packing cutoffs through several member channels. For small community-supported agriculture farms and farm-box programs, the useful goal is not to add another dashboard. It is to create a small, visible process that produces this outcome: **every eligible member change is applied before the correct packing and route cutoff or closed with a clear alternative**.

## Define the finish line first

Write the outcome in operational terms. A teammate should be able to look at one record and tell what happened, who owns the next action, and what is blocking completion. Use these rules as the boundary:

- Every open CSA member change needs one owner and a next review time
- Completion requires recorded evidence that every eligible member change is applied before the correct packing and route cutoff or closed with a clear alternative
- Automated reminders stop after verified completion or a documented closed reason
- Keep CSA subscription, payment, packing, and route system as the system of record; only necessary coordination data belongs here

## A practical end-to-end workflow

### 1. Capture the member request and effective week

Record **Member and subscription** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can apply plan rules and the relevant cutoff, or the record remains open with a reason and next action.

### 2. Apply plan rules and the relevant cutoff

Record **Delivery week and pickup site** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can approve the skip, swap, move, or alternative, or the record remains open with a reason and next action.

### 3. Approve the skip, swap, move, or alternative

Record **Request type and original message** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can update packing, inventory, payment, and route records, or the record remains open with a reason and next action.

### 4. Update packing, inventory, payment, and route records

Record **Request time and cutoff** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can confirm the final outcome to the member, or the record remains open with a reason and next action.

### 5. Confirm the final outcome to the member

Record **Eligibility and credit impact** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can close the record and review the outcome, or the record remains open with a reason and next action.

## Handle exceptions without hiding them

The process needs an explicit waiting state. Do not mark work complete because a reminder was sent or a form was opened. Keep the record open until the real exit condition is met. These events deserve a named exception path:

- a request arrives near or after its cutoff
- a swap or pickup move lacks inventory or capacity
- the member record and frozen packing list disagree

For each exception, store the reason, the next review date, and the person who can unblock it. That makes a weekly review useful instead of turning it into a search across email, chat, and spreadsheets.

## Start with one live cycle

Run the workflow for one client, location, role, order, or participant before standardizing it. At the end, remove fields nobody used, add evidence that was missing, and keep the status list short. The workflow is ready to scale when another person can operate it without asking the original owner what each row means.

## Next step

[Explore the Member Change Cutoff workflow concept](/products/member-change-cutoff) and record whether this is painful enough to justify a focused tool.
