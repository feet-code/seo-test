---
title: "How to Measure Freight Detention Evidence Tracking: Practical Metrics"
excerpt: "Definitions and calculations for useful metrics for small freight brokerages and shipper-carrier coordination teams, with concrete fields, decision rules, and implementation steps."
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

Metrics for freight detention evidence tracking should help small freight brokerages and shipper-carrier coordination teams decide what to change next. Avoid universal benchmarks: volume, service model, and exception mix differ. Establish a baseline from your own records and compare the process against itself.

## Three useful measures

| Metric | Simple calculation | Decision it supports |
|---|---|---|
| Evidence-complete time | complete evidence - request opened | improve driver and facility capture |
| Decision cycle time | decision issued - evidence complete | staff accessorial review |
| Recovery reconciliation | customer-approved amount - carrier-paid amount | find leakage and disputes |

## Capture the minimum viable data

The calculations only work if the operating record consistently includes Load, stop, facility, and parties, Appointment and appointment type, Arrival, check-in, dock, and release times, Free-time and rate terms, Tracking, BOL, or facility evidence, Delay cause and exception, Customer decision and amount, Carrier payment and billing reconciliation. Define when the clock starts and stops. Decide whether paused or waiting time remains inside cycle time, and keep that rule stable across the comparison period.

## Segment before interpreting

Separate normal work from exception-heavy work. At minimum, segment by owner, workflow stage, and closed reason. Averages can hide a small blocked queue that creates most of the follow-up burden.

## Review decisions, not dashboard colors

For each metric, write an action threshold in plain language. Examples:

- If Evidence-complete time changes materially, use it to improve driver and facility capture.
- If Decision cycle time changes materially, use it to staff accessorial review.
- If Recovery reconciliation changes materially, use it to find leakage and disputes.

Do not automate a response until a person has reviewed several examples. A high number can indicate a broken process, difficult work, or a data-definition change.

## Validate each calculation manually

Choose one closed record and calculate every metric by hand from its timestamps and statuses. Save the numerator, denominator, exclusions, and timezone rule beside the definition. Then test an abandoned record, a reopened record, and a record that spent time waiting. If two people produce different answers, the metric is not ready for a dashboard. Fix the event definitions before collecting more data.

Repeat that spot check whenever a workflow status, integration, or reporting period changes.

## A four-week measurement loop

Week one defines fields and baselines. Week two fixes missing data. Week three tests one workflow change. Week four compares the same metric definitions and reviews exceptions. Keep the change only if it improves the intended outcome without shifting work somewhere invisible.

## Next step

[Explore the Detention Evidence Desk workflow concept](/products/detention-evidence-desk) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Carrier Packet Completeness](/products/carrier-packet-completeness).
