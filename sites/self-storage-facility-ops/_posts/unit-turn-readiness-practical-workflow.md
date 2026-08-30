---
title: "Self-Storage Move-Out Inspection And Unit Turn Tracking: A Practical Workflow"
excerpt: "A step-by-step operating workflow for independent self-storage facilities and small multi-site operators, with concrete fields, decision rules, and implementation steps."
productId: "unit-turn-readiness"
productName: "Unit Turn Readiness"
generationFingerprint: "89066ee4c605764d0286"
date: "2026-08-29T21:34:11Z"
author:
  name: "John Smith"
---

A vacated unit can remain unrentable because final access, inspection, cleaning, damage, billing, and availability updates do not close as one workflow. For independent self-storage facilities and small multi-site operators, the useful goal is not to add another dashboard. It is to create a small, visible process that produces this outcome: **every vacated unit is inspected, cleared, reconciled, and published as rentable or held with a named reason**.

## Define the finish line first

Write the outcome in operational terms. A teammate should be able to look at one record and tell what happened, who owns the next action, and what is blocking completion. Use these rules as the boundary:

- Every open unit-turn task needs one owner and a next review time
- Completion requires recorded evidence that every vacated unit is inspected, cleared, reconciled, and published as rentable or held with a named reason
- Automated reminders stop after verified completion or a documented closed reason
- Keep the facility-management, access, lease, and payment platform as the system of record; only necessary coordination data belongs here

## A practical end-to-end workflow

### 1. Confirm tenant move-out and possession

Record **Facility and unit** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can inspect condition and capture evidence, or the record remains open with a reason and next action.

### 2. Inspect condition and capture evidence

Record **Tenant move-out and key or access return** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can assign cleaning, repair, or removal work, or the record remains open with a reason and next action.

### 3. Assign cleaning, repair, or removal work

Record **Inspection time and inspector** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can reconcile charges, access, and unit status, or the record remains open with a reason and next action.

### 4. Reconcile charges, access, and unit status

Record **Condition photos and findings** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can verify readiness and publish availability, or the record remains open with a reason and next action.

### 5. Verify readiness and publish availability

Record **Cleaning or repair tasks** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can close the record and review the outcome, or the record remains open with a reason and next action.

## Handle exceptions without hiding them

The process needs an explicit waiting state. Do not mark work complete because a reminder was sent or a form was opened. Keep the record open until the real exit condition is met. These events deserve a named exception path:

- a tenant reports move-out or access ends
- inspection finds damage, property, or unresolved access
- all work closes but the unit is not yet available online

For each exception, store the reason, the next review date, and the person who can unblock it. That makes a weekly review useful instead of turning it into a search across email, chat, and spreadsheets.

## Start with one live cycle

Run the workflow for one client, location, role, order, or participant before standardizing it. At the end, remove fields nobody used, add evidence that was missing, and keep the status list short. The workflow is ready to scale when another person can operate it without asking the original owner what each row means.

## Next step

[Explore the Unit Turn Readiness workflow concept](/products/unit-turn-readiness) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Delinquency Promise Board](/products/delinquency-promise-board).
