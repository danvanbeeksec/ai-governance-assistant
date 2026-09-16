// Topic.matched_elevation_rules is the table produced by the generated rule formula.
If(
    Topic.baseline_tier = "tier_1" Or CountIf(Topic.matched_elevation_rules, minimum_tier = "tier_1") > 0,
    "tier_1",
    Topic.baseline_tier = "tier_2" Or CountIf(Topic.matched_elevation_rules, minimum_tier = "tier_2") > 0,
    "tier_2",
    "tier_3"
)
