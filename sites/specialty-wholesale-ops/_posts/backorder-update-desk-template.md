---
title: "Wholesale Backorder Customer Update Tracking Template: Fields, Statuses, and Rules"
excerpt: "A practical record template for small specialty wholesalers and B2B distributors, with concrete fields, decision rules, and implementation steps."
productId: "backorder-update-desk"
productName: "Backorder Update Desk"
generationFingerprint: "63247f236e78f65404cf"
coverImage: "/assets/blog/preview/cover.jpg"
date: "2026-08-29T20:04:23Z"
author:
  name: "John Smith"
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/dynamic-routing/cover.jpg"
---

The most useful wholesale backorder customer update tracking template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

| Field | Why it exists | Update point |
|---|---|---|
| Account and order | Prevents the record from depending on memory or an inbox search | Identify affected order lines |
| Affected item and quantity | Prevents the record from depending on memory or an inbox search | Verify the latest supply evidence |
| Original promise | Prevents the record from depending on memory or an inbox search | Determine customer options |
| Latest source and timestamp | Prevents the record from depending on memory or an inbox search | Send the account-specific update |
| Current ETA | Prevents the record from depending on memory or an inbox search | Track the decision and next update |
| Partial availability | Prevents the record from depending on memory or an inbox search | Identify affected order lines |
| Approved substitute | Prevents the record from depending on memory or an inbox search | Verify the latest supply evidence |
| Customer option | Prevents the record from depending on memory or an inbox search | Determine customer options |
| Next-update date | Prevents the record from depending on memory or an inbox search | Send the account-specific update |
| Owner | Prevents the record from depending on memory or an inbox search | Track the decision and next update |

## Suggested statuses

Use workflow statuses that describe reality: **Identify Affected Order Lines → Verify The Latest Supply Evidence → Determine Customer Options → Send The Account Specific Update → Track The Decision And Next Update**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

- When an eta changes or passes its confidence window, assign a next action and review date.
- When partial stock or an approved substitute becomes available, assign a next action and review date.
- When the customer has not chosen an option before the next operational cutoff, assign a next action and review date.

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

- Half an order can ship now while the remainder has an uncertain ETA
- A substitute differs in packaging and needs buyer approval
- A supplier changes the ETA twice after the rep already contacted the customer

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

- Every ETA includes its source and freshness
- Customer options are explicit
- Substitutes are approved, not improvised
- Communication stays open until the customer decision is recorded

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

[Explore the Backorder Update Desk workflow concept](/products/backorder-update-desk) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [New Account Packet](/products/new-account-packet).
