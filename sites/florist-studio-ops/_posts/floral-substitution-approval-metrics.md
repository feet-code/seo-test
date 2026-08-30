---
title: "How to Measure Florist Substitution Approval Tracking: Practical Metrics"
excerpt: "Definitions and calculations for useful metrics for independent retail, delivery, and event floral studios, with concrete fields, decision rules, and implementation steps."
productId: "floral-substitution-approval"
productName: "Floral Substitution Approval"
generationFingerprint: "9eee4f9dbefc835e3c2c"
date: "2026-08-29T21:59:23Z"
author:
  name: "John Smith"
---

Metrics for florist substitution approval tracking should help independent retail, delivery, and event floral studios decide what to change next. Avoid universal benchmarks: volume, service model, and exception mix differ. Establish a baseline from your own records and compare the process against itself.

## Three useful measures

| Metric | Simple calculation | Decision it supports |
|---|---|---|
| Substitution decision time | decision - shortage confirmed | protect production time |
| Pre-production approval rate | material substitutions approved before design / substitutions | avoid rework |
| Margin variance | actual recipe cost - approved recipe cost | improve buying rules |

## Capture the minimum viable data

The calculations only work if the operating record consistently includes Client event order and arrangement, Original stem color grade and quantity, Shortage source and quality evidence, Substitute options and visual reference, Recipe mechanics and palette impact, Cost margin and quantity change, Designer or client decision evidence, Updated recipe purchase and production notice. Define when the clock starts and stops. Decide whether paused or waiting time remains inside cycle time, and keep that rule stable across the comparison period.

## Segment before interpreting

Separate normal work from exception-heavy work. At minimum, segment by owner, workflow stage, and closed reason. Averages can hide a small blocked queue that creates most of the follow-up burden.

## Review decisions, not dashboard colors

For each metric, write an action threshold in plain language. Examples:

- If Substitution decision time changes materially, use it to protect production time.
- If Pre-production approval rate changes materially, use it to avoid rework.
- If Margin variance changes materially, use it to improve buying rules.

Do not automate a response until a person has reviewed several examples. A high number can indicate a broken process, difficult work, or a data-definition change.

## Validate each calculation manually

Choose one closed record and calculate every metric by hand from its timestamps and statuses. Save the numerator, denominator, exclusions, and timezone rule beside the definition. Then test an abandoned record, a reopened record, and a record that spent time waiting. If two people produce different answers, the metric is not ready for a dashboard. Fix the event definitions before collecting more data.

Repeat that spot check whenever a workflow status, integration, or reporting period changes.

## A four-week measurement loop

Week one defines fields and baselines. Week two fixes missing data. Week three tests one workflow change. Week four compares the same metric definitions and reviews exceptions. Keep the change only if it improves the intended outcome without shifting work somewhere invisible.

## Next step

[Explore the Floral Substitution Approval workflow concept](/products/floral-substitution-approval) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Floral Delivery and Install Readiness](/products/floral-delivery-install-readiness).
