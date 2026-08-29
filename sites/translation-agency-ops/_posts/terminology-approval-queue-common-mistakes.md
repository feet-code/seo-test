---
title: "Common Translation Terminology Approval Workflow Mistakes and How to Prevent Them"
excerpt: "Process mistakes and guardrails for boutique translation agencies and localization project teams, with concrete fields, decision rules, and implementation steps."
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

Translators raise terminology questions in comments and messages, but client answers are not always normalized, approved, and propagated into the glossary before more work continues. The recurring failures are usually process-design problems rather than motivation problems. For boutique translation agencies and localization project teams, these are the mistakes worth finding before buying or building software.


### 1. Approving a term without source context

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Source term and context** at the point of work and enforce this guardrail: Completion requires recorded evidence that every terminology question receives an authoritative decision that is applied to the glossary and affected translation work When the exception occurs, keep it visible instead of repairing it privately in email.

### 2. Letting different reviewers approve conflicting translations

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Screenshot or segment reference** at the point of work and enforce this guardrail: Automated reminders stop after verified completion or a documented closed reason When the exception occurs, keep it visible instead of repairing it privately in email.

### 3. Closing the question before updating the glossary

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Proposed target terms** at the point of work and enforce this guardrail: Keep TMS, translation memory, glossary, and approved source files as the system of record; only necessary coordination data belongs here When the exception occurs, keep it visible instead of repairing it privately in email.

### 4. Applying a project-specific choice across all clients

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Owner and authorized approver** at the point of work and enforce this guardrail: Every open terminology decision needs one owner and a next review time When the exception occurs, keep it visible instead of repairing it privately in email.

## Audit five recent records

Pick five completed or abandoned examples and ask:

- Can we reconstruct client, project, and language pair without asking the original owner?
- Can we reconstruct source term and context without asking the original owner?
- Can we reconstruct screenshot or segment reference without asking the original owner?
- Can we reconstruct proposed target terms without asking the original owner?
- Can we reconstruct owner and authorized approver without asking the original owner?

If the answer is no, improve the capture point rather than adding a later reporting step. Reports cannot recover decisions that were never recorded.

## Use mistakes as software requirements

Turn every frequent failure into a testable requirement. “Better visibility” is vague; “show every record with no owner or next date” can be tested. “More automation” is vague; “stop reminders after the completion condition is recorded” can be tested.

## Next step

[Explore the Terminology Approval Queue workflow concept](/products/terminology-approval-queue) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Reviewer Handoff Tracker](/products/reviewer-handoff-tracker).
