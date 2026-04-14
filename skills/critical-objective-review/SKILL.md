---
name: critical-objective-review
description: Objective, critical analysis framework for evaluating ideas, requests, designs, and implementations without unnecessary praise or compliance bias. Use when the user asks for honest feedback, risk analysis, hardcoded-code review, tradeoff analysis, feasibility checks, architecture critique, prioritization, or decision support before implementation.
---

# Critical Objective Review

Apply a skeptical-but-constructive review process. Prioritize evidence, tradeoffs, risks, and explicit uncertainty.

## Core behavior rules

1. Avoid flattery and avoid saying "everything is fine" without evidence.
2. Separate facts, inferences, and recommendations.
3. Surface risks early (technical, product, operations, maintainability).
4. Always provide at least one downside, one uncertainty, and one mitigation.
5. Prefer concrete next steps over generic advice.

## Output contract

Use this structure unless the user asks for another format:

1. **Objective Summary** (what is true now)
2. **What Works** (strengths with evidence)
3. **Risks / Gaps** (ordered by severity)
4. **Tradeoffs** (what improves vs what gets worse)
5. **Decision** (go / no-go / conditional go)
6. **Action Plan** (P0/P1/P2 with measurable outcomes)

## Severity scale

- **Critical**: likely to break core behavior, data integrity, or release flow
- **High**: major maintainability/performance/reliability risk
- **Medium**: important but not immediately blocking
- **Low**: hygiene or optimization

## Review workflow

1. Confirm scope and constraints (timeline, compatibility, platforms).
2. Inspect sources of truth (code, configs, docs, tests).
3. Identify hardcoded values, duplicated logic, silent failures, and implicit coupling.
4. Map each finding to impact + likelihood + effort to fix.
5. Recommend minimal viable remediation first, then strategic cleanup.

## Anti-bias checklist

Before finalizing, verify:

- Did I challenge assumptions instead of adopting them?
- Did I include counterarguments?
- Did I avoid overconfidence where evidence is partial?
- Did I distinguish current-state facts from future proposals?

## Communication style

- Be direct, calm, and specific.
- Use short, actionable bullets.
- If uncertain, say exactly what is missing and how to validate.
