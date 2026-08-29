---
title: "Common Freight Detention Evidence Tracking Mistakes and How to Prevent Them"
excerpt: "Process mistakes and guardrails for small freight brokerages and shipper-carrier coordination teams, with concrete fields, decision rules, and implementation steps."
productId: "detention-evidence-desk"
productName: "Detention Evidence Desk"
generationFingerprint: "14e2144847e351cd03f6"
coverImage: "/assets/blog/preview/cover.jpg"
date: "2026-08-29T21:34:11Z"
author:
  name: "John Smith"
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/dynamic-routing/cover.jpg"
---

Arrival and departure times, free-time terms, driver messages, location evidence, facility acknowledgments, customer approval, and carrier payment are difficult to reconcile after a load. The recurring failures are usually process-design problems rather than motivation problems. For small freight brokerages and shipper-carrier coordination teams, these are the mistakes worth finding before buying or building software.


### 1. Using a driver text as the only time source

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Appointment and appointment type** at the point of work and enforce this guardrail: Completion requires recorded evidence that every detention request is evaluated from agreed terms and time evidence, then reconciled across customer charge and carrier payment When the exception occurs, keep it visible instead of repairing it privately in email.

### 2. Applying the wrong customer's free-time terms

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Arrival, check-in, dock, and release times** at the point of work and enforce this guardrail: Automated reminders stop after verified completion or a documented closed reason When the exception occurs, keep it visible instead of repairing it privately in email.

### 3. Approving carrier payment without customer-billing disposition

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Free-time and rate terms** at the point of work and enforce this guardrail: Keep the TMS, carrier, load, tracking, document, and billing platform as the system of record; only necessary coordination data belongs here When the exception occurs, keep it visible instead of repairing it privately in email.

### 4. Changing timestamps after a decision without history

This usually survives because the workflow records activity but not the decision that activity was meant to produce. Add **Tracking, BOL, or facility evidence** at the point of work and enforce this guardrail: Every open detention request needs one owner and a next review time When the exception occurs, keep it visible instead of repairing it privately in email.

## Audit five recent records

Pick five completed or abandoned examples and ask:

- Can we reconstruct load, stop, facility, and parties without asking the original owner?
- Can we reconstruct appointment and appointment type without asking the original owner?
- Can we reconstruct arrival, check-in, dock, and release times without asking the original owner?
- Can we reconstruct free-time and rate terms without asking the original owner?
- Can we reconstruct tracking, bol, or facility evidence without asking the original owner?

If the answer is no, improve the capture point rather than adding a later reporting step. Reports cannot recover decisions that were never recorded.

## Use mistakes as software requirements

Turn every frequent failure into a testable requirement. “Better visibility” is vague; “show every record with no owner or next date” can be tested. “More automation” is vague; “stop reminders after the completion condition is recorded” can be tested.

## Next step

[Explore the Detention Evidence Desk workflow concept](/products/detention-evidence-desk) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Carrier Packet Completeness](/products/carrier-packet-completeness).
