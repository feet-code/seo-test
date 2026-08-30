---
title: "Architectural Rfi Decision Tracking: A Practical Workflow"
excerpt: "A step-by-step operating workflow for small architecture firms and design-project administrators, with concrete fields, decision rules, and implementation steps."
productId: "rfi-decision-register"
productName: "RFI Decision Register"
generationFingerprint: "47b7db28daa17a0bd8ea"
date: "2026-08-29T21:05:26Z"
author:
  name: "John Smith"
---

RFI questions, responses, sketches, cost impacts, and drawing updates are linked imperfectly, so a answered item can still leave unresolved design work. For small architecture firms and design-project administrators, the useful goal is not to add another dashboard. It is to create a small, visible process that produces this outcome: **every RFI response identifies the authoritative decision, impact, and required document updates before operational closure**.

## Define the finish line first

Write the outcome in operational terms. A teammate should be able to look at one record and tell what happened, who owns the next action, and what is blocking completion. Use these rules as the boundary:

- Every open RFI decision needs one owner and a next review time
- Completion requires recorded evidence that every RFI response identifies the authoritative decision, impact, and required document updates before operational closure
- Automated reminders stop after verified completion or a documented closed reason
- Keep controlled drawing, specification, RFI, and submittal repository as the system of record; only necessary coordination data belongs here

## A practical end-to-end workflow

### 1. Register the question and governing references

Record **Project and RFI number** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can assign the decision owner and needed-by date, or the record remains open with a reason and next action.

### 2. Assign the decision owner and needed-by date

Record **Question and location** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can develop and approve the response, or the record remains open with a reason and next action.

### 3. Develop and approve the response

Record **Referenced drawing or specification** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can assess cost, schedule, and document impact, or the record remains open with a reason and next action.

### 4. Assess cost, schedule, and document impact

Record **Originator and responsible party** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can distribute the decision and verify follow-through, or the record remains open with a reason and next action.

### 5. Distribute the decision and verify follow-through

Record **Needed-by date** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can close the record and review the outcome, or the record remains open with a reason and next action.

## Handle exceptions without hiding them

The process needs an explicit waiting state. Do not mark work complete because a reminder was sent or a form was opened. Keep the record open until the real exit condition is met. These events deserve a named exception path:

- an RFI approaches its needed-by date without a decision
- the response changes cost, schedule, scope, or controlled documents
- field conditions or a revision supersede the published response

For each exception, store the reason, the next review date, and the person who can unblock it. That makes a weekly review useful instead of turning it into a search across email, chat, and spreadsheets.

## Start with one live cycle

Run the workflow for one client, location, role, order, or participant before standardizing it. At the end, remove fields nobody used, add evidence that was missing, and keep the status list short. The workflow is ready to scale when another person can operate it without asking the original owner what each row means.

## Next step

[Explore the RFI Decision Register workflow concept](/products/rfi-decision-register) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Consultant Deliverable Board](/products/consultant-deliverable-board).
