#!/usr/bin/env python3
"""Create deterministic, product-specific editorial probes from ideas.json context.

This is intentionally separate from the Gemini generator. It turns reviewed research
fields in ideas.json into a reproducible first content batch, while normal launches
continue to adopt the resulting posts through the existing generation fingerprints.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from generate_posts import (
    article_target,
    existing_product_posts,
    generation_fingerprint,
    load_site,
    safe_slug,
    site_products,
    write_product_posts,
)

ROOT = Path(__file__).resolve().parents[1]
IDEAS = ROOT / "ideas" / "ideas.json"


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _steps(items: list[str], fields: list[str]) -> str:
    sections = []
    for index, step in enumerate(items, 1):
        field = fields[(index - 1) % len(fields)]
        next_step = items[index] if index < len(items) else "close the record and review the outcome"
        sections.append(
            f"### {index}. {step}\n\n"
            f"Record **{field}** at this point, name the person responsible, and define the evidence that "
            f"allows the work to move to the next step. The exit condition should be observable: either "
            f"the team can {next_step.lower()}, or the record remains open with a reason and next action."
        )
    return "\n\n".join(sections)


def _field_table(fields: list[str], workflow: list[str]) -> str:
    rows = ["| Field | Why it exists | Update point |", "|---|---|---|"]
    for index, field in enumerate(fields):
        step = workflow[index % len(workflow)]
        rows.append(
            f"| {field} | Prevents the record from depending on memory or an inbox search | {step} |"
        )
    return "\n".join(rows)


def _metric_table(metrics: list[dict[str, str]]) -> str:
    rows = ["| Metric | Simple calculation | Decision it supports |", "|---|---|---|"]
    for metric in metrics:
        rows.append(
            f"| {metric['name']} | {metric['formula']} | {metric['decision']} |"
        )
    return "\n".join(rows)


def _alternative_table(alternatives: list[dict[str, str]]) -> str:
    rows = ["| Approach | Best when | Main limitation |", "|---|---|---|"]
    for alternative in alternatives:
        rows.append(
            f"| {alternative['name']} | {alternative['best']} | {alternative['limit']} |"
        )
    return "\n".join(rows)


def _automation_table(context: dict[str, Any]) -> str:
    rows = ["| Trigger | Safe automatic action | Keep a person involved when |", "|---|---|---|"]
    for index, trigger in enumerate(context["triggers"]):
        action = context["workflow"][(index + 1) % len(context["workflow"])]
        exception = context["mistakes"][index % len(context["mistakes"])]
        rows.append(f"| {trigger} | Queue or prompt: {action} | The risk is {exception.lower()} |")
    return "\n".join(rows)


def _cta(product: dict[str, Any], peer: dict[str, Any] | None) -> str:
    lines = [
        f"[Explore the {product['name']} workflow concept](/products/{product['id']}) and record whether "
        "this is painful enough to justify a focused tool."
    ]
    if peer:
        lines.append(
            f"For the adjacent workflow, see [{peer['name']}](/products/{peer['id']})."
        )
    return "\n\n".join(lines)


def _guide(product: dict[str, Any], context: dict[str, Any], peer: dict[str, Any] | None) -> str:
    return f"""{product['problem']} For {product['audience']}, the useful goal is not to add another dashboard. It is to create a small, visible process that produces this outcome: **{context['outcome']}**.

## Define the finish line first

Write the outcome in operational terms. A teammate should be able to look at one record and tell what happened, who owns the next action, and what is blocking completion. Use these rules as the boundary:

{_bullets(context['rules'])}

## A practical end-to-end workflow

{_steps(context['workflow'], context['fields'])}

## Handle exceptions without hiding them

The process needs an explicit waiting state. Do not mark work complete because a reminder was sent or a form was opened. Keep the record open until the real exit condition is met. These events deserve a named exception path:

{_bullets(context['triggers'])}

For each exception, store the reason, the next review date, and the person who can unblock it. That makes a weekly review useful instead of turning it into a search across email, chat, and spreadsheets.

## Start with one live cycle

Run the workflow for one client, location, role, order, or participant before standardizing it. At the end, remove fields nobody used, add evidence that was missing, and keep the status list short. The workflow is ready to scale when another person can operate it without asking the original owner what each row means.

## Next step

{_cta(product, peer)}"""


def _checklist(product: dict[str, Any], context: dict[str, Any], peer: dict[str, Any] | None) -> str:
    before = context["fields"][: max(2, len(context["fields"]) // 2)]
    after = context["fields"][len(before) :]
    return f"""A checklist for {product['topic']} should prevent missing decisions, not merely prove that somebody clicked boxes. The checklist below is designed for {product['audience']} and centers on one result: **{context['outcome']}**.

## Before the work starts

{_bullets([f'Confirm {item}' for item in before])}

Also name the owner and the expected completion condition. If either is unknown, the work is not ready to enter the active queue.

## While the work is moving

{_bullets([f'Update {step}' for step in context['workflow']])}

Every update should change a decision. Notes such as “followed up” are weak unless they also include the channel, result, next date, and owner.

## Before marking it complete

{_bullets([f'Verify {item}' for item in after] or [f"Verify {context['fields'][-1]}"])}

Confirm that the actual outcome—not just an activity—has been recorded. If the process ended early, use a closed reason rather than deleting the record.

## Copy-and-paste weekly review

{_bullets([f'[ ] Review records where {trigger.lower()}' for trigger in context['triggers']])}

{_bullets([f'[ ] Check for {mistake.lower()}' for mistake in context['mistakes']])}

## Make the checklist measurable

Choose one metric before the next cycle. Good options for this workflow are {', '.join(metric['name'] for metric in context['metrics'])}. A checklist that never changes a metric or prevents a known failure mode is probably administrative overhead.

## Assign ownership and escalation

Put one role—not a group—next to every item that can remain open. Define a backup owner and an escalation time for work that affects a customer, client, participant, or delivery promise. During review, separate **not started**, **waiting on someone**, and **failed validation**; those states need different actions. If a checklist item repeatedly waits on the same dependency, redesign the intake or handoff instead of adding more reminder boxes.

## Next step

{_cta(product, peer)}"""


def _template(product: dict[str, Any], context: dict[str, Any], peer: dict[str, Any] | None) -> str:
    statuses = [safe_slug(step).replace("-", " ").title() for step in context["workflow"]]
    return f"""The most useful {product['topic']} template is a small operating record. It should answer what is happening, who owns it, what evidence exists, and when the next decision occurs. This structure works in a spreadsheet, database, or focused application.

## Recommended record fields

{_field_table(context['fields'], context['workflow'])}

## Suggested statuses

Use workflow statuses that describe reality: **{' → '.join(statuses)}**. Add **Waiting** only when you also capture a waiting reason and review date. Add **Closed—Not Completed** when an item legitimately ends without the desired outcome.

## Follow-up rules

{_bullets([f'When {trigger.lower()}, assign a next action and review date.' for trigger in context['triggers']])}

Avoid reminders with no stop condition. A rule should say when it starts, who receives it, what counts as a response, and when a person should take over.

## Example records

{_bullets(context['examples'])}

For each example, write the current status, next action, owner, and supporting evidence. This makes the template testable with real work rather than idealized sample data.

## Quality-control rules

{_bullets(context['rules'])}

Before adding automation, run the template manually for a week. Remove ambiguous fields and confirm that two different users classify the same situation the same way. Consistency matters more than having a long form.

## Next step

{_cta(product, peer)}"""


def _mistakes(product: dict[str, Any], context: dict[str, Any], peer: dict[str, Any] | None) -> str:
    sections = []
    for index, mistake in enumerate(context["mistakes"], 1):
        field = context["fields"][index % len(context["fields"])]
        rule = context["rules"][index % len(context["rules"])]
        sections.append(
            f"### {index}. {mistake}\n\n"
            f"This usually survives because the workflow records activity but not the decision that activity "
            f"was meant to produce. Add **{field}** at the point of work and enforce this guardrail: {rule} "
            "When the exception occurs, keep it visible instead of repairing it privately in email."
        )
    return f"""{product['problem']} The recurring failures are usually process-design problems rather than motivation problems. For {product['audience']}, these are the mistakes worth finding before buying or building software.

{chr(10).join(chr(10) + section for section in sections)}

## Audit five recent records

Pick five completed or abandoned examples and ask:

{_bullets([f'Can we reconstruct {field.lower()} without asking the original owner?' for field in context['fields'][:5]])}

If the answer is no, improve the capture point rather than adding a later reporting step. Reports cannot recover decisions that were never recorded.

## Use mistakes as software requirements

Turn every frequent failure into a testable requirement. “Better visibility” is vague; “show every record with no owner or next date” can be tested. “More automation” is vague; “stop reminders after the completion condition is recorded” can be tested.

## Next step

{_cta(product, peer)}"""


def _spreadsheet(product: dict[str, Any], context: dict[str, Any], peer: dict[str, Any] | None) -> str:
    return f"""A spreadsheet is often the right first implementation for {product['topic']}. It is cheap, editable, and forces the team to define the workflow. The question is not whether spreadsheets are good or bad; it is when coordination costs become larger than the flexibility is worth.

## Compare the realistic options

{_alternative_table(context['alternatives'])}

## A spreadsheet is still enough when

{_bullets([f'One owner can reliably manage {step.lower()}.' for step in context['workflow'][:3]])}

It also remains a good fit when volume is low, exceptions are rare, and the team reviews the sheet at a fixed cadence.

## Signals that a focused tool may be justified

{_bullets(context['triggers'])}

The strongest signal is repeated coordination work: copying status between systems, rebuilding the same reminders, or asking people for information that should already be attached to the record.

## Run a switching-cost test

Before migrating, recreate ten current records using the candidate tool. Confirm that it supports these fields without awkward workarounds: {', '.join(context['fields'])}. Then walk one exception from start to finish. Test exports and deletion before importing the full history.

Also test permissions with a real role boundary. The person doing the work, the reviewer, and an external client or participant should not automatically see the same information. Export a sample record and confirm that its status history, attachments, and ownership remain understandable outside the vendor interface.

## Avoid the all-in-one trap

A broad platform can be valuable when workflows genuinely share data. It can also force a small team to configure modules it does not need. Compare the time required to operate the system, not the number of features on the pricing page.

## Next step

{_cta(product, peer)}"""


def _metrics(product: dict[str, Any], context: dict[str, Any], peer: dict[str, Any] | None) -> str:
    return f"""Metrics for {product['topic']} should help {product['audience']} decide what to change next. Avoid universal benchmarks: volume, service model, and exception mix differ. Establish a baseline from your own records and compare the process against itself.

## Three useful measures

{_metric_table(context['metrics'])}

## Capture the minimum viable data

The calculations only work if the operating record consistently includes {', '.join(context['fields'])}. Define when the clock starts and stops. Decide whether paused or waiting time remains inside cycle time, and keep that rule stable across the comparison period.

## Segment before interpreting

Separate normal work from exception-heavy work. At minimum, segment by owner, workflow stage, and closed reason. Averages can hide a small blocked queue that creates most of the follow-up burden.

## Review decisions, not dashboard colors

For each metric, write an action threshold in plain language. Examples:

{_bullets([f"If {metric['name']} changes materially, use it to {metric['decision'].lower()}." for metric in context['metrics']])}

Do not automate a response until a person has reviewed several examples. A high number can indicate a broken process, difficult work, or a data-definition change.

## Validate each calculation manually

Choose one closed record and calculate every metric by hand from its timestamps and statuses. Save the numerator, denominator, exclusions, and timezone rule beside the definition. Then test an abandoned record, a reopened record, and a record that spent time waiting. If two people produce different answers, the metric is not ready for a dashboard. Fix the event definitions before collecting more data.

Repeat that spot check whenever a workflow status, integration, or reporting period changes.

## A four-week measurement loop

Week one defines fields and baselines. Week two fixes missing data. Week three tests one workflow change. Week four compares the same metric definitions and reviews exceptions. Keep the change only if it improves the intended outcome without shifting work somewhere invisible.

## Next step

{_cta(product, peer)}"""


def _automation(product: dict[str, Any], context: dict[str, Any], peer: dict[str, Any] | None) -> str:
    return f"""Automation for {product['topic']} should remove predictable coordination while preserving judgment for exceptions. Start from the workflow, not from a list of integrations. For {product['audience']}, the target outcome is **{context['outcome']}**.

## Separate rules from judgment

Good automation handles deterministic actions: creating a task, calculating a due date, routing a complete record, or stopping a reminder. A person should handle ambiguity, relationship-sensitive communication, unusual risk, and conflicting evidence.

## Trigger-action-exception map

{_automation_table(context)}

## Build stop conditions first

The fastest way to make automation annoying is to send messages after the real work is complete. Every rule needs a completion condition, maximum attempt count, quiet period, owner, and manual override. Store the reason when a rule is suppressed.

## Roll out in three stages

1. **Observe:** run the proposed rule manually and record every exception.
2. **Suggest:** let software draft or queue the action while a person approves it.
3. **Automate:** allow low-risk cases to proceed and route exceptions to a named owner.

Use these operating rules during rollout:

{_bullets(context['rules'])}

## Preserve an audit trail

Store the trigger, input state, action, timestamp, and rule version for every automated step. A human reviewer should be able to reconstruct why the action occurred and reverse it without editing raw data. When a user overrides the rule, capture a short reason; repeated overrides are evidence that the automation boundary is wrong, not that users need more training.

## Measure whether automation helped

Track {', '.join(metric['name'] for metric in context['metrics'])}. Also record overrides and incorrect actions. Time saved is not useful if the process creates confusing communication or hides blocked work.

## Next step

{_cta(product, peer)}"""


def _examples(product: dict[str, Any], context: dict[str, Any], peer: dict[str, Any] | None) -> str:
    sections = []
    for index, example in enumerate(context["examples"], 1):
        trigger = context["triggers"][(index - 1) % len(context["triggers"])]
        fields = context["fields"][index - 1 : index + 2]
        sections.append(
            f"### Scenario {index}: {example}\n\n"
            f"Create the record before the first follow-up. Capture {', '.join(fields)}, then move it through "
            f"{context['workflow'][0].lower()} and {context['workflow'][1].lower()}. If {trigger.lower()}, "
            "do not improvise in a private message; assign the exception, set a review date, and preserve the "
            "evidence needed for the next decision. Close with an explicit outcome and reason."
        )
    return f"""Examples make {product['topic']} easier to design because they reveal where a neat diagram meets messy work. The scenarios below are not claims about a particular company; they are test cases {product['audience']} can run against a template or software trial.

{' '.join(sections)}

## Debrief each scenario

After running a scenario, ask:

{_bullets([f'Did the record make {rule.lower()}?' for rule in context['rules']])}

Also check whether a new teammate could identify the owner, next action, and finish condition without opening another system.

## Convert scenarios into acceptance tests

Use the normal case, waiting case, and closed-without-completion case in every software demo. Require the vendor—or your own prototype—to show the full workflow rather than isolated feature screens. Export the resulting records and verify that the status history remains understandable.

## Next step

{_cta(product, peer)}"""


def _buying_guide(product: dict[str, Any], context: dict[str, Any], peer: dict[str, Any] | None) -> str:
    return f"""Software for {product['topic']} should be evaluated against the operating problem, not a generic feature checklist. For {product['audience']}, a useful trial must demonstrate this outcome: **{context['outcome']}**.

## Write requirements from the workflow

The tool must support these steps without hidden spreadsheets: {', '.join(context['workflow'])}. It must also make these fields easy to capture at the moment work happens: {', '.join(context['fields'])}.

## Use a live demo script

Ask the vendor—or your internal prototype—to complete these tasks:

{_bullets([f'Create and resolve this test case: {example}' for example in context['examples']])}

Then test one waiting case, one reassignment, one closed-without-completion case, and one export. Do not accept a slide deck in place of the workflow.

## Score the trial

{_metric_table(context['metrics'])}

Add setup time, recurring administration, export quality, permission clarity, and mobile usability where relevant. Weight the score by frequency: a daily two-minute annoyance matters more than a rare advanced feature.

## Red flags

{_bullets(context['mistakes'])}

Also be cautious when the product requires broad process migration before it can solve the narrow problem, or when basic history/export controls are unavailable.

## Make the decision with real records

Run a small trial using current work, not sanitized sample data. Compare the realistic alternatives below and record why the winning approach fits now:

{_alternative_table(context['alternatives'])}

## Next step

{_cta(product, peer)}"""


def _alternatives(product: dict[str, Any], context: dict[str, Any], peer: dict[str, Any] | None) -> str:
    return f"""There are several valid ways to manage {product['topic']}. The right choice depends on volume, exception rate, ownership, and how much coordination crosses systems. Start with the smallest approach that keeps the work reliable.

## Option comparison

{_alternative_table(context['alternatives'])}

## Choose the manual option when

One owner can see the entire queue, the workflow changes often, and missed handoffs are rare. Document the process anyway so growth does not depend on that person's memory.

## Choose a general platform when

The team already uses it consistently and the workflow shares records with adjacent work. Confirm that statuses, reminders, and permissions can be configured without creating a second shadow spreadsheet.

## Choose a focused tool when

{_bullets(context['triggers'])}

A focused tool should reduce those specific coordination costs. If it merely presents the same data in a prettier view, the migration is unlikely to pay off.

## Run a two-week experiment

Select ten live records. Implement {', '.join(context['fields'])}, and follow this sequence: {' → '.join(context['workflow'])}. Track {', '.join(metric['name'] for metric in context['metrics'])}. At the end, review every exception and ask whether the tool made the next action clearer.

## Preserve reversibility

Export the trial data, document status definitions, and keep the previous process available until the new one completes a full cycle. A good decision is not just about features; it is about whether the team can adopt, operate, and leave the system without losing its history.

Record the decision date and the conditions that would justify reviewing the choice again.

## Next step

{_cta(product, peer)}"""


ARTICLE_BUILDERS: list[tuple[str, str, str, Callable[..., str]]] = [
    ("practical-workflow", "{topic}: A Practical Workflow", "A step-by-step operating workflow", _guide),
    ("checklist", "{topic} Checklist for {audience}", "A copyable quality-control checklist", _checklist),
    ("template", "{topic} Template: Fields, Statuses, and Rules", "A practical record template", _template),
    ("common-mistakes", "Common {topic} Mistakes and How to Prevent Them", "Process mistakes and guardrails", _mistakes),
    ("spreadsheet-vs-software", "{name} vs. a Spreadsheet: When Software Is Worth It", "A spreadsheet-versus-software decision guide", _spreadsheet),
    ("metrics", "How to Measure {topic}: Practical Metrics", "Definitions and calculations for useful metrics", _metrics),
    ("automation-guide", "How to Automate {topic} Without Losing Judgment", "A safe automation rollout guide", _automation),
    ("examples", "{topic} Examples: Three Workflow Scenarios", "Three realistic workflow test cases", _examples),
    ("software-buying-guide", "{topic} Software Buying Guide", "A trial and evaluation framework", _buying_guide),
    ("alternatives", "{topic} Alternatives: Manual, General, or Focused Tools", "A practical alternatives comparison", _alternatives),
]


def articles_for(
    product: dict[str, Any],
    context: dict[str, Any],
    peer: dict[str, Any] | None,
) -> list[dict[str, str]]:
    required_lists = {
        "workflow": 4,
        "fields": 5,
        "mistakes": 3,
        "metrics": 3,
        "alternatives": 3,
        "triggers": 3,
        "examples": 3,
        "rules": 3,
    }
    if not str(context.get("outcome", "")).strip():
        raise ValueError(f"{product['id']} probeContext needs outcome")
    for key, minimum in required_lists.items():
        value = context.get(key)
        if not isinstance(value, list) or len(value) < minimum:
            raise ValueError(f"{product['id']} probeContext.{key} needs {minimum}+ items")

    values = {
        "name": product["name"],
        "topic": str(product["topic"]).title(),
        "audience": str(product["audience"]).title(),
    }
    articles = []
    for slug, title_template, excerpt_prefix, builder in ARTICLE_BUILDERS:
        title = title_template.format(**values)
        articles.append(
            {
                "slug": slug,
                "title": title,
                "excerpt": (
                    f"{excerpt_prefix} for {product['audience']}, with concrete fields, "
                    "decision rules, and implementation steps."
                ),
                "content": builder(product, context, peer),
            }
        )
    return articles


def load_contexts() -> dict[str, dict[str, Any]]:
    document = json.loads(IDEAS.read_text(encoding="utf-8"))
    return {
        str(idea["id"]): idea["probeContext"]
        for idea in document["ideas"]
        if isinstance(idea, dict) and isinstance(idea.get("probeContext"), dict)
    }


def generate_site(site_id: str, contexts: dict[str, dict[str, Any]], *, force: bool) -> int:
    site, directory = load_site(site_id)
    products = site_products(site)
    target = article_target(site)
    if target != len(ARTICLE_BUILDERS):
        raise ValueError(
            f"{site_id} requests {target} posts/product; editorial batch provides {len(ARTICLE_BUILDERS)}"
        )
    written = 0
    for index, product in enumerate(products):
        product_id = str(product["id"])
        existing = existing_product_posts(directory, product_id)
        if len(existing) >= target and not force:
            print(f"{site_id}/{product_id}: {len(existing)} posts already exist; skipped")
            continue
        context = contexts.get(product_id)
        if context is None:
            raise ValueError(f"ideas.json has no probeContext for {product_id}")
        peers = [item for item in products if item["id"] != product_id]
        peer = peers[index % len(peers)] if peers else None
        articles = articles_for(product, context, peer)
        fingerprint = generation_fingerprint(site, product, target)
        paths = write_product_posts(site, directory, product, articles, fingerprint)
        written += len(paths)
        print(f"{site_id}/{product_id}: wrote {len(paths)} editorial probes")
    return written


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate reviewed editorial probes from ideas.json probeContext"
    )
    parser.add_argument("--site", action="append", help="Site ID; repeat as needed")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.limit < 0:
        parser.error("--limit must be zero or positive")

    contexts = load_contexts()
    configured = sorted(
        path.parent.name
        for path in (ROOT / "sites").glob("*/site.json")
        if json.loads(path.read_text(encoding="utf-8")).get("portfolioManaged")
    )
    selected = args.site or configured
    unknown = set(selected) - set(configured)
    if unknown:
        parser.error("unknown portfolio site(s): " + ", ".join(sorted(unknown)))
    if args.limit:
        selected = selected[: args.limit]
    total = sum(generate_site(site_id, contexts, force=args.force) for site_id in selected)
    print(f"Editorial batch complete: {total} new probes across {len(selected)} sites")


if __name__ == "__main__":
    main()
