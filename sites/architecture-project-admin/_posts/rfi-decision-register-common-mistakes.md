---
title: "Common Architectural Rfi Decision Tracking Mistakes and How to Prevent Them"
excerpt: "Process mistakes and guardrails for small architecture firms and design-project administrators, with concrete fields, decision rules, and implementation steps."
productId: "rfi-decision-register"
productName: "RFI Decision Register"
generationFingerprint: "47b7db28daa17a0bd8ea"
coverImage: "/assets/blog/preview/cover.jpg"
date: "2026-08-29T21:05:26Z"
author:
  name: "John Smith"
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/dynamic-routing/cover.jpg"
---

RFI questions, responses, sketches, cost impacts, and drawing updates are linked imperfectly, so a answered item can still leave unresolved design work. The recurring failures are usually process-design problems rather than motivation problems. For small architecture firms and design-project administrators, these are the mistakes worth finding before buying or building software.


### 1. Closing when a response is posted but drawings still conflict

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Question and location** at the point of work and enforce this guardrail: Completion requires recorded evidence that every RFI response identifies the authoritative decision, impact, and required document updates before operational closure When the exception occurs, keep it visible instead of repairing it privately in email.

### 2. Answering a different question than the cited condition

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Referenced drawing or specification** at the point of work and enforce this guardrail: Automated reminders stop after verified completion or a documented closed reason When the exception occurs, keep it visible instead of repairing it privately in email.

### 3. Letting an informal field direction bypass the register

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Originator and responsible party** at the point of work and enforce this guardrail: Keep controlled drawing, specification, RFI, and submittal repository as the system of record; only necessary coordination data belongs here When the exception occurs, keep it visible instead of repairing it privately in email.

### 4. Overwriting a response without marking the superseded version

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Needed-by date** at the point of work and enforce this guardrail: Every open RFI decision needs one owner and a next review time When the exception occurs, keep it visible instead of repairing it privately in email.

## Audit five recent records

Pick five completed or abandoned examples and ask:

- Can we reconstruct project and rfi number without asking the original owner?
- Can we reconstruct question and location without asking the original owner?
- Can we reconstruct referenced drawing or specification without asking the original owner?
- Can we reconstruct originator and responsible party without asking the original owner?
- Can we reconstruct needed-by date without asking the original owner?

If the answer is no, improve the capture point rather than adding a later reporting step. Reports cannot recover decisions that were never recorded.

## Use mistakes as software requirements

Turn every frequent failure into a testable requirement. “Better visibility” is vague; “show every record with no owner or next date” can be tested. “More automation” is vague; “stop reminders after the completion condition is recorded” can be tested.

## Next step

[Explore the RFI Decision Register workflow concept](/products/rfi-decision-register) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Consultant Deliverable Board](/products/consultant-deliverable-board).
