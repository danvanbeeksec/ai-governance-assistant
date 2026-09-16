// Generated display fields for the chat response.
{
    matched_elevation_rules_text: If(
        IsEmpty(Topic.matched_elevation_rules),
        "None",
        Concat(Topic.matched_elevation_rules, rule_id & " | " & reason, Char(10))
    ),
    enterprise_dependencies_text: Concat(
        Filter(Topic.control_outcomes, section = "enterprise_dependencies"),
        control_id & " | " & title & " | Follow-up: " & follow_up,
        Char(10)
    ),
    applicable_system_controls_text: Concat(
        Filter(Topic.control_outcomes, section = "system_controls" And outcome = "applicable"),
        control_id & " | " & title,
        Char(10)
    ),
    undetermined_system_controls_text: Concat(
        Filter(Topic.control_outcomes, section = "system_controls" And outcome = "undetermined"),
        control_id & " | " & title & " | Follow-up: " & follow_up,
        Char(10)
    )
}
