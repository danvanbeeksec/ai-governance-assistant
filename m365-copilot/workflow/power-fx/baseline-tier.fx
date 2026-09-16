// Generated from the canonical risk model. Do not edit manually.
Switch(
    Topic.autonomy_level & "|" & Topic.information_sensitivity,
    "autonomous|confidential", "tier_1",
    "autonomous|internal", "tier_2",
    "autonomous|public", "tier_2",
    "autonomous|restricted", "tier_1",
    "conditionally_autonomous|confidential", "tier_2",
    "conditionally_autonomous|internal", "tier_3",
    "conditionally_autonomous|public", "tier_3",
    "conditionally_autonomous|restricted", "tier_1",
    "human_supervised|confidential", "tier_3",
    "human_supervised|internal", "tier_3",
    "human_supervised|public", "tier_3",
    "human_supervised|restricted", "tier_1",
    Blank()
)
