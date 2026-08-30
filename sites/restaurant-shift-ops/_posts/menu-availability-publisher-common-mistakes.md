---
title: "Common Restaurant 86 List And Menu Availability Tracking Mistakes and How to Prevent Them"
excerpt: "Process mistakes and guardrails for independent restaurants and small multi-location restaurant groups, with concrete fields, decision rules, and implementation steps."
productId: "menu-availability-publisher"
productName: "Menu Availability Publisher"
generationFingerprint: "cef19eb8d1d46b337eed"
date: "2026-08-29T21:34:11Z"
author:
  name: "John Smith"
---

When an item or modifier sells out, staff may update one POS screen but miss online ordering, third-party channels, service teams, or the later un-86 decision. The recurring failures are usually process-design problems rather than motivation problems. For independent restaurants and small multi-location restaurant groups, these are the mistakes worth finding before buying or building software.


### 1. 86ing the parent item but not affected modifiers

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Menu item or modifier** at the point of work and enforce this guardrail: Completion requires recorded evidence that every availability change is approved, published to all intended channels, acknowledged by service staff, and reversed only after supply is verified When the exception occurs, keep it visible instead of repairing it privately in email.

### 2. Updating the POS but not online channels

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Reason and remaining quantity** at the point of work and enforce this guardrail: Automated reminders stop after verified completion or a documented closed reason When the exception occurs, keep it visible instead of repairing it privately in email.

### 3. Un-86ing from an expected delivery rather than verified stock

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Unavailable-from and expected return** at the point of work and enforce this guardrail: Keep the POS, inventory, recipe, scheduling, and maintenance systems as the system of record; only necessary coordination data belongs here When the exception occurs, keep it visible instead of repairing it privately in email.

### 4. Leaving servers to discover the change from failed orders

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Affected channels** at the point of work and enforce this guardrail: Every open menu availability change needs one owner and a next review time When the exception occurs, keep it visible instead of repairing it privately in email.

## Audit five recent records

Pick five completed or abandoned examples and ask:

- Can we reconstruct location and shift without asking the original owner?
- Can we reconstruct menu item or modifier without asking the original owner?
- Can we reconstruct reason and remaining quantity without asking the original owner?
- Can we reconstruct unavailable-from and expected return without asking the original owner?
- Can we reconstruct affected channels without asking the original owner?

If the answer is no, improve the capture point rather than adding a later reporting step. Reports cannot recover decisions that were never recorded.

## Use mistakes as software requirements

Turn every frequent failure into a testable requirement. “Better visibility” is vague; “show every record with no owner or next date” can be tested. “More automation” is vague; “stop reminders after the completion condition is recorded” can be tested.

## Next step

[Explore the Menu Availability Publisher workflow concept](/products/menu-availability-publisher) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Manager Shift Handoff](/products/manager-shift-handoff).
