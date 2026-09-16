# Guided intake

Use the canonical field list and allowed values returned by `scripts/assess.py requirements`. The descriptions below translate those values into user-facing language; they do not add fields or change the risk model.

## Interview pattern

Do not repeat facts already supplied. A practical default is three short rounds:

1. Identity: system name, business purpose, and accountable owner.
2. Authority: autonomy, human review, action authority, and system access.
3. Exposure: information sensitivity, external reach, reversibility, decision impact, and agent capabilities.

If a response is ambiguous, propose the closest supported value, explain why, and request confirmation. Preserve the user's correction. Never silently choose a more favorable value.

## Supported choices

### Autonomy

- `human_supervised`: A person reviews each meaningful action before it takes effect.
- `conditionally_autonomous`: The system can act within boundaries, with checkpoints or exception handling.
- `autonomous`: The system can take meaningful actions without routine prior approval.

### Information sensitivity

- `public`: Approved for public disclosure.
- `internal`: Nonpublic internal information with ordinary handling requirements.
- `confidential`: Sensitive business, customer, employee, contractual, or similar information.
- `restricted`: The organization's highest sensitivity category or specially protected data.

Use the organization's classification if the user knows it. Otherwise describe the proposed category and request confirmation.

### Human review

- `prior_to_each_meaningful_action`: Review occurs before every meaningful action or outcome.
- `checkpoints_or_exceptions`: Review occurs at defined checkpoints or when exceptions arise.
- `no_prior_review`: Meaningful action may occur before a person reviews it.

### Action authority

- `generate_only`: Produces content or analysis without recommending or changing a system.
- `recommend`: Recommends a decision or action for someone else to take.
- `modify_nonproduction`: Can change development, test, or other nonproduction environments.
- `modify_production`: Can change production systems, records, configurations, or workflows.
- `execute_material_transaction`: Can move money, enter commitments, grant benefits, or execute another material transaction.
- `safety_relevant_action`: Can affect physical, health, security, or other safety-relevant outcomes.

Choose the most consequential permitted action, not the most common action.

### System access

- `none`: No authenticated access to organizational systems.
- `standard`: Ordinary user or service access with bounded permissions.
- `privileged`: Administrative, elevated, or otherwise powerful access.

### External reach

- `none`: No interaction beyond the immediate internal environment.
- `bounded`: Interaction with a defined external group, service, or channel.
- `broad`: Public, open-ended, or large-scale external interaction.

### Reversibility

- `easy`: Material effects can be promptly and reliably reversed.
- `recoverable_with_effort`: Recovery is possible but requires meaningful time, cost, coordination, or remediation.
- `difficult`: Material effects may be irreversible or exceptionally difficult to remediate.

### Decision impact

- `none`: No meaningful decision or operational impact.
- `operational`: Can affect ordinary business operations or service delivery.
- `consequential`: Can materially affect people, finances, access, rights, safety, or important business outcomes.
- `regulated_or_consequential`: Used in a regulated decision or another decision with comparable significance.

### Agent capabilities

Select every enabled capability, or confirm an empty list:

- `external_tools`: Invokes tools, APIs, code, plugins, or connected services.
- `external_communication`: Sends messages or publishes content outside the immediate system.
- `delegation`: Assigns work to or coordinates with another AI system or agent.
- `persistent_memory`: Retains task, user, conversational, vector, episodic, or cross-session state.

## Inference boundary

A proposed interpretation is not a fact until the user confirms it. For example:

> You said the assistant can send customer emails after an employee approves each message. I would record `external_communication` as enabled, `external_reach` as `bounded`, and human review as `prior_to_each_meaningful_action`. Please confirm or correct those values.

Do not infer information sensitivity, consequential impact, privileged access, or regulated use merely from an industry label.
