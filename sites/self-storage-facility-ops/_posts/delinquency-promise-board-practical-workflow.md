---
title: "Self-Storage Delinquency Follow-Up Tracking: A Practical Workflow"
excerpt: "A step-by-step operating workflow for independent self-storage facilities and small multi-site operators, with concrete fields, decision rules, and implementation steps."
productId: "delinquency-promise-board"
productName: "Delinquency Promise Board"
generationFingerprint: "e6792f9ff583a53ae077"
date: "2026-08-29T21:34:11Z"
author:
  name: "John Smith"
---

Payment reminders, tenant promises, access changes, policy milestones, and manager exceptions are recorded in different places, making the next compliant action hard to see. For independent self-storage facilities and small multi-site operators, the useful goal is not to add another dashboard. It is to create a small, visible process that produces this outcome: **every delinquent account has a policy-based next action, documented tenant response, and verified stop condition**.

## Define the finish line first

Write the outcome in operational terms. A teammate should be able to look at one record and tell what happened, who owns the next action, and what is blocking completion. Use these rules as the boundary:

- Every open delinquent tenant action needs one owner and a next review time
- Completion requires recorded evidence that every delinquent account has a policy-based next action, documented tenant response, and verified stop condition
- Automated reminders stop after verified completion or a documented closed reason
- Keep the facility-management, access, lease, and payment platform as the system of record; only necessary coordination data belongs here

## A practical end-to-end workflow

### 1. Open the delinquency action from the account ledger

Record **Facility, tenant, unit, and lease** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can apply the current facility policy and milestone, or the record remains open with a reason and next action.

### 2. Apply the current facility policy and milestone

Record **Balance and aging date** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can contact the tenant through the approved channel, or the record remains open with a reason and next action.

### 3. Contact the tenant through the approved channel

Record **Policy version and current milestone** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can record a payment, promise, dispute, move-out, or escalation, or the record remains open with a reason and next action.

### 4. Record a payment, promise, dispute, move-out, or escalation

Record **Notice channel and delivery evidence** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can verify the ledger and access outcome before closure, or the record remains open with a reason and next action.

### 5. Verify the ledger and access outcome before closure

Record **Tenant response and promise date** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can close the record and review the outcome, or the record remains open with a reason and next action.

## Handle exceptions without hiding them

The process needs an explicit waiting state. Do not mark work complete because a reminder was sent or a form was opened. Keep the record open until the real exit condition is met. These events deserve a named exception path:

- a balance reaches the next policy milestone
- a tenant makes or misses a payment promise
- payment, access, or move-out status changes in another system

For each exception, store the reason, the next review date, and the person who can unblock it. That makes a weekly review useful instead of turning it into a search across email, chat, and spreadsheets.

## Start with one live cycle

Run the workflow for one client, location, role, order, or participant before standardizing it. At the end, remove fields nobody used, add evidence that was missing, and keep the status list short. The workflow is ready to scale when another person can operate it without asking the original owner what each row means.

## Next step

[Explore the Delinquency Promise Board workflow concept](/products/delinquency-promise-board) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Unit Turn Readiness](/products/unit-turn-readiness).
