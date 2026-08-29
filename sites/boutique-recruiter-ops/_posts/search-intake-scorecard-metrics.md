---
title: "How to Measure Recruiting Search Intake And Candidate Calibration Scorecards: Practical Metrics"
excerpt: "Definitions and calculations for useful metrics for independent recruiters and boutique recruiting firms, with concrete fields, decision rules, and implementation steps."
productId: "search-intake-scorecard"
productName: "Search Intake Scorecard"
generationFingerprint: "7cb5ad03fde7b2e6e454"
coverImage: "/assets/blog/preview/cover.jpg"
date: "2026-08-29T20:04:23Z"
author:
  name: "John Smith"
  picture: "/assets/blog/authors/jj.jpeg"
ogImage:
  url: "/assets/blog/dynamic-routing/cover.jpg"
---

Metrics for recruiting search intake and candidate calibration scorecards should help independent recruiters and boutique recruiting firms decide what to change next. Avoid universal benchmarks: volume, service model, and exception mix differ. Establish a baseline from your own records and compare the process against itself.

## Three useful measures

| Metric | Simple calculation | Decision it supports |
|---|---|---|
| Calibration change count | criteria changes after sourcing begins | identify unstable or underspecified searches |
| Submission acceptance rate | candidates advanced / candidates submitted | test whether recruiter and client are aligned |
| Decision turnaround | decision timestamp - submission timestamp | surface client feedback bottlenecks |

## Capture the minimum viable data

The calculations only work if the operating record consistently includes Role outcome, Must-have criteria, Flexible criteria, Acceptable evidence, Disqualifiers, Compensation boundary, Interview owners, Calibration notes. Define when the clock starts and stops. Decide whether paused or waiting time remains inside cycle time, and keep that rule stable across the comparison period.

## Segment before interpreting

Separate normal work from exception-heavy work. At minimum, segment by owner, workflow stage, and closed reason. Averages can hide a small blocked queue that creates most of the follow-up burden.

## Review decisions, not dashboard colors

For each metric, write an action threshold in plain language. Examples:

- If Calibration change count changes materially, use it to identify unstable or underspecified searches.
- If Submission acceptance rate changes materially, use it to test whether recruiter and client are aligned.
- If Decision turnaround changes materially, use it to surface client feedback bottlenecks.

Do not automate a response until a person has reviewed several examples. A high number can indicate a broken process, difficult work, or a data-definition change.

## Validate each calculation manually

Choose one closed record and calculate every metric by hand from its timestamps and statuses. Save the numerator, denominator, exclusions, and timezone rule beside the definition. Then test an abandoned record, a reopened record, and a record that spent time waiting. If two people produce different answers, the metric is not ready for a dashboard. Fix the event definitions before collecting more data.

Repeat that spot check whenever a workflow status, integration, or reporting period changes.

## A four-week measurement loop

Week one defines fields and baselines. Week two fixes missing data. Week three tests one workflow change. Week four compares the same metric definitions and reviews exceptions. Keep the change only if it improves the intended outcome without shifting work somewhere invisible.

## Next step

[Explore the Search Intake Scorecard workflow concept](/products/search-intake-scorecard) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Interview Debrief Collector](/products/interview-debrief-collector).
