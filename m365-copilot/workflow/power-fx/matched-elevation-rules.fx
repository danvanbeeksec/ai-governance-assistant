// Topic.agent_capabilities_token must use |value| delimiters.
Filter(
    Table(
    { rule_id: "ER-001", minimum_tier: "tier_1", reason: "Material, production, or safety-relevant action can occur without prior human approval.", matched: And(
            Or(
            Topic.action_authority = "modify_production",
            Topic.action_authority = "execute_material_transaction",
            Topic.action_authority = "safety_relevant_action"
        ),
            Or(
            Topic.human_review = "checkpoints_or_exceptions",
            Topic.human_review = "no_prior_review"
        )
        ) },
    { rule_id: "ER-002", minimum_tier: "tier_2", reason: "Privileged access is combined with an agent capability that expands reach or persistence.", matched: And(
            Or(
            "|external_tools|" in Topic.agent_capabilities_token,
            "|external_communication|" in Topic.agent_capabilities_token,
            "|delegation|" in Topic.agent_capabilities_token,
            "|persistent_memory|" in Topic.agent_capabilities_token
        ),
            Topic.system_access = "privileged"
        ) },
    { rule_id: "ER-003", minimum_tier: "tier_1", reason: "Consequential impact is difficult to reverse after it occurs.", matched: And(
            Or(
            Topic.decision_impact = "consequential",
            Topic.decision_impact = "regulated_or_consequential"
        ),
            Topic.reversibility = "difficult"
        ) },
    { rule_id: "ER-004", minimum_tier: "tier_1", reason: "A regulated or consequential decision can occur without prior human review.", matched: And(
            Topic.decision_impact = "regulated_or_consequential",
            Or(
            Topic.human_review = "checkpoints_or_exceptions",
            Topic.human_review = "no_prior_review"
        )
        ) },
    { rule_id: "ER-005", minimum_tier: "tier_1", reason: "Autonomous external communication has broad reach.", matched: And(
            "|external_communication|" in Topic.agent_capabilities_token,
            Topic.autonomy_level = "autonomous",
            Topic.external_reach = "broad"
        ) },
    { rule_id: "ER-006", minimum_tier: "tier_1", reason: "Restricted information always requires Tier 1 governance.", matched: Topic.information_sensitivity = "restricted" },
    { rule_id: "ER-007", minimum_tier: "tier_1", reason: "Autonomous operation involving Confidential information requires Tier 1 governance.", matched: And(
            Topic.autonomy_level = "autonomous",
            Topic.information_sensitivity = "confidential"
        ) }
    ),
    matched
)
