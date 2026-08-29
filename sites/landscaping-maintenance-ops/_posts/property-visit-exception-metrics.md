---
title: "How to Measure Landscape Maintenance Visit Exception Tracking: Practical Metrics"
excerpt: "Definitions and calculations for useful metrics for small commercial landscaping and recurring property-maintenance companies, with concrete fields, decision rules, and implementation steps."
productId: "property-visit-exception"
productName: "Property Visit Exception"
generationFingerprint: "74b5353a963af3660cfa"
coverImage: "/assets/blog/preview/cover.jpg"
date: "2026-08-29T21:59:23Z"
author:
  name: "John Smith"
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/dynamic-routing/cover.jpg"
---

Metrics for landscape maintenance visit exception tracking should help small commercial landscaping and recurring property-maintenance companies decide what to change next. Avoid universal benchmarks: volume, service model, and exception mix differ. Establish a baseline from your own records and compare the process against itself.

## Three useful measures

| Metric | Simple calculation | Decision it supports |
|---|---|---|
| Complete-visit rate | visits with all contracted scope / visits attempted | adjust routes and staffing |
| Recovery lead time | recovery completion - exception time | reserve capacity |
| Repeat property exception | properties with repeated same blocker / properties with exceptions | solve root causes |

## Capture the minimum viable data

The calculations only work if the operating record consistently includes Customer property and contract, Visit date crew and route, Planned service scope, Completed and skipped tasks, Exception cause and evidence, Contract billing or credit treatment, Customer notice and recovery owner, Recovery completion or closed reason. Define when the clock starts and stops. Decide whether paused or waiting time remains inside cycle time, and keep that rule stable across the comparison period.

## Segment before interpreting

Separate normal work from exception-heavy work. At minimum, segment by owner, workflow stage, and closed reason. Averages can hide a small blocked queue that creates most of the follow-up burden.

## Review decisions, not dashboard colors

For each metric, write an action threshold in plain language. Examples:

- If Complete-visit rate changes materially, use it to adjust routes and staffing.
- If Recovery lead time changes materially, use it to reserve capacity.
- If Repeat property exception changes materially, use it to solve root causes.

Do not automate a response until a person has reviewed several examples. A high number can indicate a broken process, difficult work, or a data-definition change.

## Validate each calculation manually

Choose one closed record and calculate every metric by hand from its timestamps and statuses. Save the numerator, denominator, exclusions, and timezone rule beside the definition. Then test an abandoned record, a reopened record, and a record that spent time waiting. If two people produce different answers, the metric is not ready for a dashboard. Fix the event definitions before collecting more data.

Repeat that spot check whenever a workflow status, integration, or reporting period changes.

## A four-week measurement loop

Week one defines fields and baselines. Week two fixes missing data. Week three tests one workflow change. Week four compares the same metric definitions and reviews exceptions. Keep the change only if it improves the intended outcome without shifting work somewhere invisible.

## Next step

[Explore the Property Visit Exception workflow concept](/products/property-visit-exception) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Enhancement Approval Desk](/products/enhancement-approval-desk).
