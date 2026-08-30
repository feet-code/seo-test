---
title: "How to Measure Candidate Follow-Up Tracking For Recruiting Agencies: Practical Metrics"
excerpt: "Definitions and calculations for useful metrics for independent recruiters and boutique recruiting firms, with concrete fields, decision rules, and implementation steps."
productId: "candidate-followup-desk"
productName: "Candidate Follow-Up Desk"
generationFingerprint: "01cf122a04a7f42de54c"
date: "2026-08-29T20:04:23Z"
author:
  name: "John Smith"
---

Metrics for candidate follow-up tracking for recruiting agencies should help independent recruiters and boutique recruiting firms decide what to change next. Avoid universal benchmarks: volume, service model, and exception mix differ. Establish a baseline from your own records and compare the process against itself.

## Three useful measures

| Metric | Simple calculation | Decision it supports |
|---|---|---|
| Promise kept rate | promised updates delivered on time / promised updates due | find where candidate commitments break |
| Open follow-up age | current date - oldest unresolved next-contact date | prioritize neglected relationships |
| Response outcome mix | count by advanced, waiting, declined, or no response | adjust message timing and channel |

## Capture the minimum viable data

The calculations only work if the operating record consistently includes Candidate and role, Last meaningful contact, Promised update, Next-contact date, Channel, Owner, Response outcome, Closed reason. Define when the clock starts and stops. Decide whether paused or waiting time remains inside cycle time, and keep that rule stable across the comparison period.

## Segment before interpreting

Separate normal work from exception-heavy work. At minimum, segment by owner, workflow stage, and closed reason. Averages can hide a small blocked queue that creates most of the follow-up burden.

## Review decisions, not dashboard colors

For each metric, write an action threshold in plain language. Examples:

- If Promise kept rate changes materially, use it to find where candidate commitments break.
- If Open follow-up age changes materially, use it to prioritize neglected relationships.
- If Response outcome mix changes materially, use it to adjust message timing and channel.

Do not automate a response until a person has reviewed several examples. A high number can indicate a broken process, difficult work, or a data-definition change.

## Validate each calculation manually

Choose one closed record and calculate every metric by hand from its timestamps and statuses. Save the numerator, denominator, exclusions, and timezone rule beside the definition. Then test an abandoned record, a reopened record, and a record that spent time waiting. If two people produce different answers, the metric is not ready for a dashboard. Fix the event definitions before collecting more data.

Repeat that spot check whenever a workflow status, integration, or reporting period changes.

## A four-week measurement loop

Week one defines fields and baselines. Week two fixes missing data. Week three tests one workflow change. Week four compares the same metric definitions and reviews exceptions. Keep the change only if it improves the intended outcome without shifting work somewhere invisible.

## Next step

[Explore the Candidate Follow-Up Desk workflow concept](/products/candidate-followup-desk) and record whether this is painful enough to justify a focused tool.

For the adjacent workflow, see [Search Intake Scorecard](/products/search-intake-scorecard).
