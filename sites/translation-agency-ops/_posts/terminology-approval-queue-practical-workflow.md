---
title: "Translation Terminology Approval Workflow: A Practical Workflow"
excerpt: "A step-by-step operating workflow for boutique translation agencies and localization project teams, with concrete fields, decision rules, and implementation steps."
productId: "terminology-approval-queue"
productName: "Terminology Approval Queue"
generationFingerprint: "f9edb42facc71cd2e0ee"
coverImage: "/assets/blog/preview/cover.jpg"
date: "2026-08-29T21:05:26Z"
author:
  name: "John Smith"
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/dynamic-routing/cover.jpg"
---

Translators raise terminology questions in comments and messages, but client answers are not always normalized, approved, and propagated into the glossary before more work continues. For boutique translation agencies and localization project teams, the useful goal is not to add another dashboard. It is to create a small, visible process that produces this outcome: **every terminology question receives an authoritative decision that is applied to the glossary and affected translation work**.

## Define the finish line first

Write the outcome in operational terms. A teammate should be able to look at one record and tell what happened, who owns the next action, and what is blocking completion. Use these rules as the boundary:

- Every open terminology decision needs one owner and a next review time
- Completion requires recorded evidence that every terminology question receives an authoritative decision that is applied to the glossary and affected translation work
- Automated reminders stop after verified completion or a documented closed reason
- Keep TMS, translation memory, glossary, and approved source files as the system of record; only necessary coordination data belongs here

## A practical end-to-end workflow

### 1. Open the source term with context

Record **Client, project, and language pair** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can propose target terms and rationale, or the record remains open with a reason and next action.

### 2. Propose target terms and rationale

Record **Source term and context** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can route to the authorized reviewer, or the record remains open with a reason and next action.

### 3. Route to the authorized reviewer

Record **Screenshot or segment reference** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can record the approved or rejected decision, or the record remains open with a reason and next action.

### 4. Record the approved or rejected decision

Record **Proposed target terms** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can update language assets and notify affected work, or the record remains open with a reason and next action.

### 5. Update language assets and notify affected work

Record **Owner and authorized approver** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can close the record and review the outcome, or the record remains open with a reason and next action.

## Handle exceptions without hiding them

The process needs an explicit waiting state. Do not mark work complete because a reminder was sent or a form was opened. Keep the record open until the real exit condition is met. These events deserve a named exception path:

- a term blocks active translation near its needed-by time
- reviewers provide conflicting answers
- an approved term changes after work has already used it

For each exception, store the reason, the next review date, and the person who can unblock it. That makes a weekly review useful instead of turning it into a search across email, chat, and spreadsheets.

## Start with one live cycle

Run the workflow for one client, location, role, order, or participant before standardizing it. At the end, remove fields nobody used, add evidence that was missing, and keep the status list short. The workflow is ready to scale when another person can operate it without asking the original owner what each row means.

## Next step

[Explore the Terminology Approval Queue workflow concept](/products/terminology-approval-queue) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Reviewer Handoff Tracker](/products/reviewer-handoff-tracker).
