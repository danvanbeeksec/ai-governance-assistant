# Tenant build and export runbook

This runbook assembles the offline kit into a Microsoft Copilot Studio solution. Perform it in a commercial Microsoft 365 tenant using synthetic information only.

Microsoft changes Copilot Studio labels periodically. If a label differs, use the current equivalent described in the linked Microsoft documentation rather than changing the design.

## 1. Prerequisites

- Microsoft Copilot Studio access in the intended Power Platform environment
- Permission to create agents and unmanaged solutions
- Permission to upload an embedded knowledge file
- Permission to publish to the Microsoft 365 Copilot and Teams channel
- A Microsoft 365 administrator who can approve the organizational catalog submission
- The complete `m365-copilot` transfer-kit folder

No custom connector, MCP endpoint, Azure resource, service account, API key, SharePoint site, OneDrive folder, or Dataverse assessment table is required.

## 2. Verify the transferred package

Confirm that `package-manifest.json` reports:

- Framework library version `1.2.0`
- Framework lifecycle status `published`
- Risk model `ai-governance-inherent-risk` version `0.1.0`
- Applicability methodology `ai-control-applicability` version `1.0.0` with status `approved`
- `external_runtime_required` is `false`
- `inventory_persistence` is `false`

If Python is available on the device, run this inside the transferred `m365-copilot` folder:

```powershell
python verify_package.py
```

Do not continue if an integrity check fails.

## 3. Create the unmanaged solution

1. Open Copilot Studio and select the intended environment.
2. Open **Solutions**.
3. Create an unmanaged solution named `AI Governance Assessment`.
4. Use an organization-controlled publisher. A suggested prefix is `aigov`.
5. Record the solution version as `0.1.0`.

Create and maintain every agent component inside this solution. Before export, use **Add required objects** so topics, knowledge, and dependent objects travel with the agent. Microsoft documents this requirement in [Export and import agents using solutions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-import-export).

## 4. Create the agent

1. Create an agent named `AI Governance Assessment` in the solution.
2. Description: `Conducts a structured, deterministic inherent-risk assessment and identifies applicable, inherited, and undetermined AI governance controls.`
3. Configure the agent to authenticate with Microsoft.
4. Do not enable anonymous access.
5. Paste the contents of `agent/instructions.md` into the agent instructions.
6. Add the entries from `agent/conversation-starters.json` as suggested prompts.
7. Enable generative orchestration for conversational intake and knowledge-based control explanations. Keep all tiering and control outcomes in the deterministic topic described below.

## 5. Add embedded knowledge

1. Add `knowledge/control-catalog.txt` as an uploaded knowledge source.
2. Name it `AI Governance Assessment Reference`.
3. Describe it as: `Authoritative control, evidence, provenance, risk-model, and applicability reference for the AI Governance Assessment agent.`
4. Do not add employer documents, private standards mappings, or tenant content.
5. Verify that the file is included when required solution objects are added.

The reference file is about 90 KB and is well below Microsoft's current embedded-file limit. Microsoft documents uploaded and embedded knowledge in [Add knowledge sources to a declarative agent](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-add-knowledge).

## 6. Create the deterministic evaluation topic

Create a topic named `Evaluate AI Governance Facts`. Its purpose is to evaluate twelve normalized and user-confirmed inputs. Do not let generative answers calculate or override the result.

### Topic inputs

Create these text input variables. Use the field descriptions and allowed values in `workflow/assessment-engine.json`:

- `system_name`
- `business_purpose`
- `accountable_owner`
- `autonomy_level`
- `information_sensitivity`
- `human_review`
- `action_authority`
- `system_access`
- `external_reach`
- `reversibility`
- `decision_impact`
- `agent_capabilities`

Set the topic so it requires explicit values rather than dynamically filling sensitive or ambiguous fields from model inference.

### Formula sequence

Add **Set a variable value** nodes in this order. Microsoft documents this node and the `Topic.` variable prefix in [Create expressions using Power Fx](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-power-fx).

1. Create `Topic.agent_capabilities_token` and set it to:

   ```powerfx
   If(
       IsBlank(Topic.agent_capabilities),
       "||",
       "|" & Substitute(Topic.agent_capabilities, ",", "|") & "|"
   )
   ```

2. Create `Topic.baseline_tier` and paste `workflow/power-fx/baseline-tier.fx` into the formula editor.
3. Create `Topic.matched_elevation_rules` and paste `workflow/power-fx/matched-elevation-rules.fx`.
4. Create `Topic.final_tier` and paste `workflow/power-fx/final-tier.fx`.
5. Create `Topic.control_outcomes` and paste `workflow/power-fx/control-outcomes.fx`.
6. Create `Topic.report_fields` and paste `workflow/power-fx/report-fields.fx`.

Do not manually change the formulas to produce a preferred tier or smaller control set. Change the canonical model and regenerate the package instead.

### Topic outputs

Expose these output variables:

- `baseline_tier`
- `matched_elevation_rules`
- `final_tier`
- `control_outcomes`
- `report_fields`

The topic must not contain Dataverse, SharePoint, OneDrive, SQL, HTTP, custom-connector, email, approval, or ticketing actions.

## 7. Create the guided assessment topic

Create a topic named `Run AI Governance Assessment` with trigger phrases such as:

- `assess an AI use case`
- `run an AI governance assessment`
- `classify AI risk`
- `which AI controls apply`

Build the topic in this order:

1. Send the safety and decision-support notice from `agent/instructions.md`.
2. Add an **Ask with Adaptive Card** node.
3. Paste `agent/adaptive-cards/assessment-form.json` into the JSON editor. Copilot Studio automatically creates output variables from the input identifiers. See [Ask with Adaptive Cards](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-ask-with-adaptive-card).
4. Verify that the generated output variables exactly match the twelve assessment field names plus `confirmed`.
5. Add a condition requiring `confirmed` to equal `true`. If it is not true, explain that explicit confirmation is required and return to the card.
6. Redirect to `Evaluate AI Governance Facts`, mapping the twelve card outputs to the twelve topic inputs.
7. Add a message node based on `agent/report-template.md`. Use the message editor's variable picker for every `Topic.` value instead of typing variable placeholders as plain text.
8. End the topic without saving answers or creating a business record.

## 8. Add control explanation behavior

The agent instructions direct control questions to the embedded reference. Test at least one valid and one invalid identifier.

- For a valid identifier, the response must remain grounded in `control-catalog.txt`.
- For an invalid identifier, the agent must say that the control is not present.
- The agent must not invent a mapping, authority, requirement, or evidence expectation.

If the agent does not reliably use the knowledge source, add a focused topic named `Explain AI Governance Control` and configure a generative-answer node restricted to `AI Governance Assessment Reference`.

## 9. Add design comparison behavior

Create a topic named `Compare AI Designs`.

1. Explain that each option must be complete and confirmed independently.
2. Present the assessment card for option A and redirect the normalized values to `Evaluate AI Governance Facts`.
3. Copy option A's `final_tier` and applicable control identifiers into option-A variables.
4. Present the same assessment card for option B and run the evaluation topic again.
5. Report both final tiers.
6. Calculate added applicable controls as option B minus option A and removed applicable controls as option A minus option B.
7. State that the comparison does not cover cost, performance, architecture quality, residual risk, or legal compliance.

If table-difference authoring is impractical in the tenant interface, treat comparison as a post-0.1.0 enhancement. Do not claim comparison support until the acceptance test passes.

## 10. Configure data and authentication controls

1. Keep Microsoft authentication enabled.
2. Review the environment data-loss-prevention policy.
3. Confirm that no connector or action can persist assessment answers.
4. Review conversation transcript, audit, analytics, diagnostic, retention, and eDiscovery settings with the tenant administrator.
5. Update the agent privacy notice if the tenant's retention practices require more specific language.
6. Do not claim that session-only application design overrides Microsoft tenant retention.

## 11. Test before export

Complete every test in `validation-checklist.md`. Use only the synthetic scenarios in `tests/acceptance-scenarios.json`.

Do not export a release package when:

- Any expected tier differs
- Any expected elevation rule is missing or an unexpected rule appears
- Formula errors are visible
- A required field can be skipped
- The agent invents a missing fact
- A control without a matched trigger is described as unnecessary
- An action writes an assessment record
- Framework provenance is missing

## 12. Add required objects and export

1. Return to the unmanaged solution.
2. Select the agent and use **Advanced > Add required objects**.
3. Confirm that the agent, all topics, the embedded knowledge resource, and any solution-aware dependencies appear.
4. Run the solution checker if available.
5. Export an **unmanaged** solution and retain it as the editable source artifact.
6. Export a **managed** solution for controlled installation into other environments.
7. Record the exported filenames and SHA-256 digests in the GitHub release notes.

Do not commit tenant secrets, connection details, conversation transcripts, or assessment data to GitHub.

## 13. Install and publish

1. Import the managed solution into the target Power Platform environment.
2. Open the imported agent and reconfigure user authentication if prompted. Microsoft notes that authentication must be configured again after import.
3. Publish the agent.
4. Add the Microsoft 365 Copilot and Teams channel and enable availability in Microsoft 365 Copilot.
5. Submit the agent for tenant administrator approval in the organizational catalog.
6. Run the acceptance tests again in Microsoft 365 Copilot after installation.

Microsoft documents Microsoft 365 Copilot and Teams distribution in [Publish agents for Microsoft 365 Copilot](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/publish) and [Connect an agent for Teams and Microsoft 365 Copilot](https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-add-bot-to-microsoft-teams).
