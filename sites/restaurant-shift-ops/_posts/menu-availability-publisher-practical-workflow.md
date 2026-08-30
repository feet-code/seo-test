---
title: "Restaurant 86 List And Menu Availability Tracking: A Practical Workflow"
excerpt: "A step-by-step operating workflow for independent restaurants and small multi-location restaurant groups, with concrete fields, decision rules, and implementation steps."
productId: "menu-availability-publisher"
productName: "Menu Availability Publisher"
generationFingerprint: "cef19eb8d1d46b337eed"
coverImage: "/assets/blog/preview/cover.jpg"
date: "2026-08-29T21:34:11Z"
author:
  name: "John Smith"
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/dynamic-routing/cover.jpg"
---

When an item or modifier sells out, staff may update one POS screen but miss online ordering, third-party channels, service teams, or the later un-86 decision. For independent restaurants and small multi-location restaurant groups, the useful goal is not to add another dashboard. It is to create a small, visible process that produces this outcome: **every availability change is approved, published to all intended channels, acknowledged by service staff, and reversed only after supply is verified**.

## Define the finish line first

Write the outcome in operational terms. A teammate should be able to look at one record and tell what happened, who owns the next action, and what is blocking completion. Use these rules as the boundary:

- Every open menu availability change needs one owner and a next review time
- Completion requires recorded evidence that every availability change is approved, published to all intended channels, acknowledged by service staff, and reversed only after supply is verified
- Automated reminders stop after verified completion or a documented closed reason
- Keep the POS, inventory, recipe, scheduling, and maintenance systems as the system of record; only necessary coordination data belongs here

## A practical end-to-end workflow

### 1. Open the item availability change

Record **Location and shift** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can confirm item, modifier, location, and expected duration, or the record remains open with a reason and next action.

### 2. Confirm item, modifier, location, and expected duration

Record **Menu item or modifier** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can approve guest-facing wording and alternatives, or the record remains open with a reason and next action.

### 3. Approve guest-facing wording and alternatives

Record **Reason and remaining quantity** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can publish across pos, online, and team channels, or the record remains open with a reason and next action.

### 4. Publish across POS, online, and team channels

Record **Unavailable-from and expected return** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can verify live state and schedule reactivation review, or the record remains open with a reason and next action.

### 5. Verify live state and schedule reactivation review

Record **Affected channels** at this point, name the person responsible, and define the evidence that allows the work to move to the next step. The exit condition should be observable: either the team can close the record and review the outcome, or the record remains open with a reason and next action.

## Handle exceptions without hiding them

The process needs an explicit waiting state. Do not mark work complete because a reminder was sent or a form was opened. Keep the record open until the real exit condition is met. These events deserve a named exception path:

- an item cannot support expected demand
- one channel differs from the approved availability state
- verified supply returns or the expected return time passes

For each exception, store the reason, the next review date, and the person who can unblock it. That makes a weekly review useful instead of turning it into a search across email, chat, and spreadsheets.

## Start with one live cycle

Run the workflow for one client, location, role, order, or participant before standardizing it. At the end, remove fields nobody used, add evidence that was missing, and keep the status list short. The workflow is ready to scale when another person can operate it without asking the original owner what each row means.

## Next step

[Explore the Menu Availability Publisher workflow concept](/products/menu-availability-publisher) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Manager Shift Handoff](/products/manager-shift-handoff).
