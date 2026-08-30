---
title: "Tutoring Makeup Session Scheduling: A Practical Workflow"
excerpt: "A step-by-step operating workflow for independent tutoring centers and multi-tutor education businesses, with concrete fields, decision rules, and implementation steps."
productId: "makeup-session-coordinator"
productName: "Makeup Session Coordinator"
generationFingerprint: "b583c6deaa720572443e"
date: "2026-08-29T21:05:26Z"
author:
  name: "John Smith"
---

Canceled sessions create credits and promises that are hard to reconcile across tutor calendars, parent messages, attendance records, and billing rules. For independent tutoring centers and multi-tutor education businesses, the useful goal is not to add another dashboard. It is to create a small, visible process that produces this outcome: **every eligible canceled session is rescheduled, credited, expired by policy, or closed with parent acknowledgment**.

## Define the finish line first

Write the outcome in operational terms. A teammate should be able to look at one record and tell what happened, who owns the next action, and what is blocking completion. Use these rules as the boundary:

- Every open makeup session obligation needs one owner and a next review time
- Completion requires recorded evidence that every eligible canceled session is rescheduled, credited, expired by policy, or closed with parent acknowledgment
- Automated reminders stop after verified completion or a documented closed reason
- Keep tutoring schedule and student record system as the system of record; only necessary coordination data belongs here

## A practical end-to-end workflow

### 1. Record the canceled session and policy reason

Record **Student and subject** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can determine makeup or credit eligibility, or the record remains open with a reason and next action.

### 2. Determine makeup or credit eligibility

Record **Original session and tutor** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can offer compatible tutor and student times, or the record remains open with a reason and next action.

### 3. Offer compatible tutor and student times

Record **Cancellation party and time** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can confirm the replacement session, or the record remains open with a reason and next action.

### 4. Confirm the replacement session

Record **Policy and eligibility result** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can reconcile attendance, credit, and billing, or the record remains open with a reason and next action.

### 5. Reconcile attendance, credit, and billing

Record **Credit quantity and expiration** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can close the record and review the outcome, or the record remains open with a reason and next action.

## Handle exceptions without hiding them

The process needs an explicit waiting state. Do not mark work complete because a reminder was sent or a form was opened. Keep the record open until the real exit condition is met. These events deserve a named exception path:

- an eligible cancellation has no accepted option
- a credit approaches its policy expiration
- the confirmed tutor or student becomes unavailable again

For each exception, store the reason, the next review date, and the person who can unblock it. That makes a weekly review useful instead of turning it into a search across email, chat, and spreadsheets.

## Start with one live cycle

Run the workflow for one client, location, role, order, or participant before standardizing it. At the end, remove fields nobody used, add evidence that was missing, and keep the status list short. The workflow is ready to scale when another person can operate it without asking the original owner what each row means.

## Next step

[Explore the Makeup Session Coordinator workflow concept](/products/makeup-session-coordinator) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Parent Progress Publisher](/products/parent-progress-publisher).
