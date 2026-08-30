---
title: "How to Measure Septic Disposal Ticket And Pump Record Reconciliation: Practical Metrics"
excerpt: "Definitions and calculations for useful metrics for small septic pumping, inspection, and liquid-waste service companies, with concrete fields, decision rules, and implementation steps."
productId: "disposal-ticket-reconciliation"
productName: "Disposal Ticket Reconciliation"
generationFingerprint: "319f2a94a04dacc4627c"
date: "2026-08-29T21:59:23Z"
author:
  name: "John Smith"
---

Metrics for septic disposal ticket and pump record reconciliation should help small septic pumping, inspection, and liquid-waste service companies decide what to change next. Avoid universal benchmarks: volume, service model, and exception mix differ. Establish a baseline from your own records and compare the process against itself.

## Three useful measures

| Metric | Simple calculation | Decision it supports |
|---|---|---|
| Matched-load rate | loads fully reconciled / loads disposed | staff daily review |
| Ticket receipt time | ticket recorded - disposal time | improve driver capture |
| Volume variance | absolute accepted volume - linked source volume | find measurement or entry issues |

## Capture the minimum viable data

The calculations only work if the operating record consistently includes Truck driver and load, Source jobs properties and pump records, Volume by job and total, Departure and facility arrival times, Disposal facility and ticket number, Accepted volume fee and ticket image, Variance reason and reviewer, Billing and accounting release. Define when the clock starts and stops. Decide whether paused or waiting time remains inside cycle time, and keep that rule stable across the comparison period.

## Segment before interpreting

Separate normal work from exception-heavy work. At minimum, segment by owner, workflow stage, and closed reason. Averages can hide a small blocked queue that creates most of the follow-up burden.

## Review decisions, not dashboard colors

For each metric, write an action threshold in plain language. Examples:

- If Matched-load rate changes materially, use it to staff daily review.
- If Ticket receipt time changes materially, use it to improve driver capture.
- If Volume variance changes materially, use it to find measurement or entry issues.

Do not automate a response until a person has reviewed several examples. A high number can indicate a broken process, difficult work, or a data-definition change.

## Validate each calculation manually

Choose one closed record and calculate every metric by hand from its timestamps and statuses. Save the numerator, denominator, exclusions, and timezone rule beside the definition. Then test an abandoned record, a reopened record, and a record that spent time waiting. If two people produce different answers, the metric is not ready for a dashboard. Fix the event definitions before collecting more data.

Repeat that spot check whenever a workflow status, integration, or reporting period changes.

## A four-week measurement loop

Week one defines fields and baselines. Week two fixes missing data. Week three tests one workflow change. Week four compares the same metric definitions and reviews exceptions. Keep the change only if it improves the intended outcome without shifting work somewhere invisible.

## Next step

[Explore the Disposal Ticket Reconciliation workflow concept](/products/disposal-ticket-reconciliation) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Septic Site Access Readiness](/products/septic-site-access-readiness).
