---
title: "Architecture Consultant Deliverable Tracking: A Practical Workflow"
excerpt: "A step-by-step operating workflow for small architecture firms and design-project administrators, with concrete fields, decision rules, and implementation steps."
productId: "consultant-deliverable-board"
productName: "Consultant Deliverable Board"
generationFingerprint: "42ab794d9922f5e43c20"
date: "2026-08-29T21:05:26Z"
author:
  name: "John Smith"
---

Structural, MEP, civil, landscape, and specialist deliverables arrive through separate transmittals, making current version, review status, and drawing dependencies difficult to see. For small architecture firms and design-project administrators, the useful goal is not to add another dashboard. It is to create a small, visible process that produces this outcome: **every consultant deliverable is received to the agreed milestone, reviewed against dependencies, and incorporated into the controlled project set**.

## Define the finish line first

Write the outcome in operational terms. A teammate should be able to look at one record and tell what happened, who owns the next action, and what is blocking completion. Use these rules as the boundary:

- Every open consultant deliverable needs one owner and a next review time
- Completion requires recorded evidence that every consultant deliverable is received to the agreed milestone, reviewed against dependencies, and incorporated into the controlled project set
- Automated reminders stop after verified completion or a documented closed reason
- Keep controlled drawing, specification, RFI, and submittal repository as the system of record; only necessary coordination data belongs here

## A practical end-to-end workflow

### 1. Define the consultant package and milestone

Record **Project and consultant** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can request and receive the controlled transmittal, or the record remains open with a reason and next action.

### 2. Request and receive the controlled transmittal

Record **Discipline and deliverable package** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can check completeness, version, and coordination scope, or the record remains open with a reason and next action.

### 3. Check completeness, version, and coordination scope

Record **Milestone and due date** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can resolve review comments and conflicts, or the record remains open with a reason and next action.

### 4. Resolve review comments and conflicts

Record **Expected format and model version** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can accept the package and update dependent project documents, or the record remains open with a reason and next action.

### 5. Accept the package and update dependent project documents

Record **Transmittal and received time** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can close the record and review the outcome, or the record remains open with a reason and next action.

## Handle exceptions without hiding them

The process needs an explicit waiting state. Do not mark work complete because a reminder was sent or a form was opened. Keep the record open until the real exit condition is met. These events deserve a named exception path:

- a milestone deliverable is missing or incomplete
- the submitted version conflicts with another discipline
- a consultant revision changes a previously coordinated dependency

For each exception, store the reason, the next review date, and the person who can unblock it. That makes a weekly review useful instead of turning it into a search across email, chat, and spreadsheets.

## Start with one live cycle

Run the workflow for one client, location, role, order, or participant before standardizing it. At the end, remove fields nobody used, add evidence that was missing, and keep the status list short. The workflow is ready to scale when another person can operate it without asking the original owner what each row means.

## Next step

[Explore the Consultant Deliverable Board workflow concept](/products/consultant-deliverable-board) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [RFI Decision Register](/products/rfi-decision-register).
