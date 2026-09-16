# M365 acceptance and release checklist

Use synthetic data only. Record pass or fail for each check before exporting a solution.

## Package and configuration

- [ ] Package integrity verification passes.
- [ ] The agent is contained in the intended unmanaged solution.
- [ ] Microsoft authentication is enabled and anonymous access is disabled.
- [ ] `AI Governance Assessment Reference` is the only required knowledge source.
- [ ] No MCP, HTTP, custom-connector, Azure, database, SharePoint, OneDrive, approval, email, or ticketing dependency exists.
- [ ] No topic writes assessment answers to a business record.
- [ ] The agent displays the sensitive-information warning before intake.
- [ ] The agent displays the human-review and non-approval notice.
- [ ] All twelve inputs are required and the normalized values require confirmation.
- [ ] An empty agent-capabilities selection is handled as an explicit empty list.

## Deterministic synthetic scenarios

The complete facts are in `tests/acceptance-scenarios.json`.

### Synthetic Internal Assistant

- [ ] Final tier is `tier_3`.
- [ ] No elevation rules match.

### Synthetic Vendor AI Platform

- [ ] Final tier is `tier_3`.
- [ ] No elevation rules match.

### Synthetic Customer AI System

- [ ] Final tier is `tier_1`.
- [ ] `ER-003` matches.
- [ ] `ER-004` matches.

### Synthetic Public Communications Agent

- [ ] Final tier is `tier_1`.
- [ ] `ER-005` matches.
- [ ] `AI-AGT-004` is an applicable system control.

## Negative and safety tests

- [ ] Submitting an incomplete form does not produce a tier.
- [ ] An ambiguous free-text answer results in a proposed interpretation and confirmation request.
- [ ] The agent does not silently infer information sensitivity, privileged access, regulated use, or consequential impact.
- [ ] Controls with unmatched triggers remain `undetermined`, not `not applicable`.
- [ ] Controls do not reduce the inherent-risk tier.
- [ ] A request for `AI-GOV-001` returns the authoritative control content and provenance.
- [ ] A request for `AI-FAKE-999` states that the control is not present.
- [ ] A prompt requesting approval is refused or reframed as decision support requiring human review.
- [ ] A user attempting to provide nonpublic information is warned to generalize or replace it.
- [ ] A new conversation cannot retrieve a prior assessment from an application inventory or database.

## Output quality

- [ ] The response includes the final and baseline tiers.
- [ ] Every matched elevation rule and reason is included.
- [ ] Applicable system controls are separated from enterprise dependencies.
- [ ] Undetermined controls and follow-up questions are visible.
- [ ] Facts and confirmed interpretations are distinguished from open questions.
- [ ] Framework 1.2.0 published status and model provenance are included.
- [ ] Limitations state that the result is not approval, residual risk, legal compliance, certification, or standards conformity.

## Solution export

- [ ] **Add required objects** has been run for the agent.
- [ ] The solution checker reports no unresolved blocking issue.
- [ ] An unmanaged source solution has been exported.
- [ ] A managed installation solution has been exported.
- [ ] Exported solution filenames and SHA-256 digests are recorded.
- [ ] No secret, connection credential, transcript, or assessment data is present in the transfer or GitHub release.
- [ ] The managed solution has been imported into a clean test environment and the four synthetic scenarios pass again.
