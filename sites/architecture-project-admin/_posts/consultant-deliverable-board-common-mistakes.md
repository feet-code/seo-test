---
title: "Common Architecture Consultant Deliverable Tracking Mistakes and How to Prevent Them"
excerpt: "Process mistakes and guardrails for small architecture firms and design-project administrators, with concrete fields, decision rules, and implementation steps."
productId: "consultant-deliverable-board"
productName: "Consultant Deliverable Board"
generationFingerprint: "42ab794d9922f5e43c20"
coverImage: "/assets/blog/preview/cover.jpg"
date: "2026-08-29T21:05:26Z"
author:
  name: "John Smith"
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/dynamic-routing/cover.jpg"
---

Structural, MEP, civil, landscape, and specialist deliverables arrive through separate transmittals, making current version, review status, and drawing dependencies difficult to see. The recurring failures are usually process-design problems rather than motivation problems. For small architecture firms and design-project administrators, these are the mistakes worth finding before buying or building software.


### 1. Reviewing a file without preserving its transmittal

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Discipline and deliverable package** at the point of work and enforce this guardrail: Completion requires recorded evidence that every consultant deliverable is received to the agreed milestone, reviewed against dependencies, and incorporated into the controlled project set When the exception occurs, keep it visible instead of repairing it privately in email.

### 2. Treating received as coordinated

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Milestone and due date** at the point of work and enforce this guardrail: Automated reminders stop after verified completion or a documented closed reason When the exception occurs, keep it visible instead of repairing it privately in email.

### 3. Marking comments resolved without checking the revised package

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Expected format and model version** at the point of work and enforce this guardrail: Keep controlled drawing, specification, RFI, and submittal repository as the system of record; only necessary coordination data belongs here When the exception occurs, keep it visible instead of repairing it privately in email.

### 4. Using a consultant version that differs from the controlled project set

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Transmittal and received time** at the point of work and enforce this guardrail: Every open consultant deliverable needs one owner and a next review time When the exception occurs, keep it visible instead of repairing it privately in email.

## Audit five recent records

Pick five completed or abandoned examples and ask:

- Can we reconstruct project and consultant without asking the original owner?
- Can we reconstruct discipline and deliverable package without asking the original owner?
- Can we reconstruct milestone and due date without asking the original owner?
- Can we reconstruct expected format and model version without asking the original owner?
- Can we reconstruct transmittal and received time without asking the original owner?

If the answer is no, improve the capture point rather than adding a later reporting step. Reports cannot recover decisions that were never recorded.

## Use mistakes as software requirements

Turn every frequent failure into a testable requirement. “Better visibility” is vague; “show every record with no owner or next date” can be tested. “More automation” is vague; “stop reminders after the completion condition is recorded” can be tested.

## Next step

[Explore the Consultant Deliverable Board workflow concept](/products/consultant-deliverable-board) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [RFI Decision Register](/products/rfi-decision-register).
