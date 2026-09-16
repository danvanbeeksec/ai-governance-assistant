// Generated control outcomes. Absence of a trigger remains undetermined.
Table(
    { control_id: "AI-GOV-001", title: "AI governance mandate and decision rights", section: "enterprise_dependencies", outcome: "inherited_dependency", follow_up: "Confirm the enterprise provider, inheritance scope, required configuration, exclusions, evidence, and review period." },
    { control_id: "AI-GOV-002", title: "AI policy and acceptable-use boundaries", section: "enterprise_dependencies", outcome: "inherited_dependency", follow_up: "Confirm the enterprise provider, inheritance scope, required configuration, exclusions, evidence, and review period." },
    { control_id: "AI-GOV-003", title: "AI inventory and accountable ownership", section: "system_controls", outcome: "applicable", follow_up: "" },
    { control_id: "AI-GOV-004", title: "AI risk and impact assessment", section: "system_controls", outcome: "applicable", follow_up: "" },
    { control_id: "AI-GOV-005", title: "Competence and role-based awareness", section: "enterprise_dependencies", outcome: "inherited_dependency", follow_up: "Confirm the enterprise provider, inheritance scope, required configuration, exclusions, evidence, and review period." },
    { control_id: "AI-GOV-006", title: "Independent challenge and continual improvement", section: "enterprise_dependencies", outcome: "inherited_dependency", follow_up: "Confirm the enterprise provider, inheritance scope, required configuration, exclusions, evidence, and review period." },
    { control_id: "AI-SEC-001", title: "Secure architecture and threat modeling", section: "system_controls", outcome: If(
            Or(
                    Or(
                    Topic.external_reach = "bounded",
                    Topic.external_reach = "broad"
                ),
                    Or(
                    Topic.system_access = "standard",
                    Topic.system_access = "privileged"
                )
                ),
            "applicable",
            "undetermined"
        ), follow_up: "Is the system developed, integrated, configured, or otherwise exposed to trust-boundary threats?" },
    { control_id: "AI-SEC-002", title: "Identity, authentication, and least privilege", section: "system_controls", outcome: If(
            Or(
                    Or(
                    Topic.information_sensitivity = "internal",
                    Topic.information_sensitivity = "confidential",
                    Topic.information_sensitivity = "restricted"
                ),
                    Or(
                    Topic.system_access = "standard",
                    Topic.system_access = "privileged"
                ),
                    "|external_tools|" in Topic.agent_capabilities_token
                ),
            "applicable",
            "undetermined"
        ), follow_up: "Does the system authenticate users or non-human actors or access protected services?" },
    { control_id: "AI-SEC-003", title: "Untrusted input and prompt-injection defenses", section: "system_controls", outcome: If(
            Or(
                    "|external_tools|" in Topic.agent_capabilities_token,
                    "|external_communication|" in Topic.agent_capabilities_token
                ),
            "applicable",
            "undetermined"
        ), follow_up: "Does the system receive prompts, files, retrieved content, messages, web content, or other untrusted input?" },
    { control_id: "AI-SEC-004", title: "Safe output handling", section: "system_controls", outcome: "applicable", follow_up: "" },
    { control_id: "AI-SEC-005", title: "Secure development, testing, and vulnerability management", section: "system_controls", outcome: "undetermined", follow_up: "Is the system internally developed, materially integrated, configured, or customized?" },
    { control_id: "AI-SEC-006", title: "Resource and service abuse protection", section: "system_controls", outcome: If(
            Or(
                    Or(
                    Topic.autonomy_level = "autonomous",
                    Topic.autonomy_level = "conditionally_autonomous"
                ),
                    Or(
                    "|external_tools|" in Topic.agent_capabilities_token,
                    "|delegation|" in Topic.agent_capabilities_token,
                    "|persistent_memory|" in Topic.agent_capabilities_token
                ),
                    Or(
                    Topic.external_reach = "bounded",
                    Topic.external_reach = "broad"
                ),
                    Or(
                    Topic.action_authority = "modify_production",
                    Topic.action_authority = "execute_material_transaction",
                    Topic.action_authority = "safety_relevant_action"
                )
                ),
            "applicable",
            "undetermined"
        ), follow_up: "Is the system production, usage-priced, recursive, or computationally intensive?" },
    { control_id: "AI-DAT-001", title: "Authorized data use and minimization", section: "system_controls", outcome: "applicable", follow_up: "" },
    { control_id: "AI-DAT-002", title: "Data classification and protection", section: "system_controls", outcome: If(
            Or(
                    Topic.information_sensitivity = "internal",
                    Topic.information_sensitivity = "confidential",
                    Topic.information_sensitivity = "restricted"
                ),
            "applicable",
            "undetermined"
        ), follow_up: "Does the system process personal, regulated, contractual, or otherwise specially protected information?" },
    { control_id: "AI-DAT-003", title: "Data provenance, quality, and permitted sourcing", section: "system_controls", outcome: "undetermined", follow_up: "What material data and knowledge sources does the system use, and for what purpose?" },
    { control_id: "AI-DAT-004", title: "Privacy assessment and individual protections", section: "system_controls", outcome: If(
            Or(
                    Topic.decision_impact = "consequential",
                    Topic.decision_impact = "regulated_or_consequential"
                ),
            "applicable",
            "undetermined"
        ), follow_up: "Does the system use personal data or identify, profile, infer about, or materially affect individuals?" },
    { control_id: "AI-LCM-001", title: "Intended use, limitations, and success criteria", section: "system_controls", outcome: "applicable", follow_up: "" },
    { control_id: "AI-LCM-002", title: "Evaluation, validation, and release readiness", section: "system_controls", outcome: "applicable", follow_up: "" },
    { control_id: "AI-LCM-003", title: "Material change and reassessment", section: "system_controls", outcome: "applicable", follow_up: "" },
    { control_id: "AI-LCM-004", title: "Suspension and retirement", section: "system_controls", outcome: If(
            Or(
                    Or(
                    Topic.information_sensitivity = "internal",
                    Topic.information_sensitivity = "confidential",
                    Topic.information_sensitivity = "restricted"
                ),
                    Or(
                    Topic.external_reach = "bounded",
                    Topic.external_reach = "broad"
                ),
                    Or(
                    Topic.decision_impact = "operational",
                    Topic.decision_impact = "consequential",
                    Topic.decision_impact = "regulated_or_consequential"
                )
                ),
            "applicable",
            "undetermined"
        ), follow_up: "Will the system be production, externally used, vendor-dependent, or retain data?" },
    { control_id: "AI-AGT-001", title: "Agent identity and delegated authority", section: "system_controls", outcome: If(
            Or(
                    Or(
                    Topic.autonomy_level = "autonomous",
                    Topic.autonomy_level = "conditionally_autonomous"
                ),
                    Or(
                    "|external_tools|" in Topic.agent_capabilities_token,
                    "|external_communication|" in Topic.agent_capabilities_token,
                    "|delegation|" in Topic.agent_capabilities_token,
                    "|persistent_memory|" in Topic.agent_capabilities_token
                ),
                    Or(
                    Topic.action_authority = "modify_nonproduction",
                    Topic.action_authority = "modify_production",
                    Topic.action_authority = "execute_material_transaction",
                    Topic.action_authority = "safety_relevant_action"
                )
                ),
            "applicable",
            "undetermined"
        ), follow_up: "Can the system plan, invoke services, or act beyond content generation?" },
    { control_id: "AI-AGT-002", title: "Tool, connector, and action boundaries", section: "system_controls", outcome: If(
            Or(
                    "|external_tools|" in Topic.agent_capabilities_token,
                    Or(
                    Topic.system_access = "standard",
                    Topic.system_access = "privileged"
                ),
                    Or(
                    Topic.action_authority = "modify_nonproduction",
                    Topic.action_authority = "modify_production",
                    Topic.action_authority = "execute_material_transaction",
                    Topic.action_authority = "safety_relevant_action"
                )
                ),
            "applicable",
            "undetermined"
        ), follow_up: "Does the system have plugins, code execution, messaging, workflow, or other connector access?" },
    { control_id: "AI-AGT-003", title: "Human approval and irreversible-action safeguards", section: "system_controls", outcome: If(
            Or(
                    Or(
                    Topic.action_authority = "modify_nonproduction",
                    Topic.action_authority = "modify_production",
                    Topic.action_authority = "execute_material_transaction",
                    Topic.action_authority = "safety_relevant_action"
                ),
                    "|external_communication|" in Topic.agent_capabilities_token,
                    Topic.reversibility = "difficult"
                ),
            "applicable",
            "undetermined"
        ), follow_up: "Can the system make commitments, affect rights, send messages, execute code, or move value?" },
    { control_id: "AI-AGT-004", title: "Agent memory and state protection", section: "system_controls", outcome: If(
            "|persistent_memory|" in Topic.agent_capabilities_token,
            "applicable",
            "undetermined"
        ), follow_up: "Does the system retain any conversational, task, user, vector, episodic, or cross-session state?" },
    { control_id: "AI-AGT-005", title: "Multi-agent and delegation controls", section: "system_controls", outcome: If(
            "|delegation|" in Topic.agent_capabilities_token,
            "applicable",
            "undetermined"
        ), follow_up: "Can the system communicate, coordinate, negotiate, or invoke another AI system?" },
    { control_id: "AI-AGT-006", title: "Agent containment and emergency stop", section: "system_controls", outcome: If(
            Or(
                    Or(
                    Topic.autonomy_level = "autonomous",
                    Topic.autonomy_level = "conditionally_autonomous"
                ),
                    Topic.system_access = "privileged",
                    Topic.external_reach = "broad",
                    Or(
                    Topic.action_authority = "modify_production",
                    Topic.action_authority = "execute_material_transaction",
                    Topic.action_authority = "safety_relevant_action"
                ),
                    Topic.reversibility = "difficult"
                ),
            "applicable",
            "undetermined"
        ), follow_up: "Could delayed containment materially increase harm?" },
    { control_id: "AI-OPS-001", title: "Logging and traceability", section: "system_controls", outcome: "undetermined", follow_up: "Will the system operate in production, and what events and decisions require traceability?" },
    { control_id: "AI-OPS-002", title: "Behavioral and control monitoring", section: "system_controls", outcome: "undetermined", follow_up: "Will the system operate in production, and could delayed detection materially increase harm?" },
    { control_id: "AI-OPS-003", title: "AI incident response and reporting", section: "system_controls", outcome: "applicable", follow_up: "" },
    { control_id: "AI-OPS-004", title: "Resilience, safe failure, and recovery", section: "system_controls", outcome: If(
            Or(
                    Or(
                    Topic.decision_impact = "operational",
                    Topic.decision_impact = "consequential",
                    Topic.decision_impact = "regulated_or_consequential"
                ),
                    Or(
                    Topic.external_reach = "bounded",
                    Topic.external_reach = "broad"
                ),
                    Or(
                    Topic.action_authority = "modify_production",
                    Topic.action_authority = "execute_material_transaction",
                    Topic.action_authority = "safety_relevant_action"
                ),
                    Or(
                    Topic.reversibility = "recoverable_with_effort",
                    Topic.reversibility = "difficult"
                )
                ),
            "applicable",
            "undetermined"
        ), follow_up: "Does the system support material operations or have availability or integrity requirements?" },
    { control_id: "AI-VSC-001", title: "AI supplier and service due diligence", section: "system_controls", outcome: "undetermined", follow_up: "Which external models, applications, platforms, data services, plugins, or support providers are involved?" },
    { control_id: "AI-VSC-002", title: "Contractual AI safeguards", section: "system_controls", outcome: "undetermined", follow_up: "Does a third party process organizational data or support material operations?" },
    { control_id: "AI-VSC-003", title: "Component provenance and integrity", section: "system_controls", outcome: "undetermined", follow_up: "Does the system use external, open-source, pretrained, downloaded, imported, or dynamically loaded components?" },
    { control_id: "AI-VSC-004", title: "Supplier change and subprocessor oversight", section: "system_controls", outcome: "undetermined", follow_up: "Which providers and subprocessors can materially change the system or service?" },
    { control_id: "AI-VSC-005", title: "Concentration, continuity, and exit planning", section: "system_controls", outcome: "undetermined", follow_up: "Could loss or material change of a provider, model, platform, or data source disrupt important operations or controls?" },
    { control_id: "AI-GOV-007", title: "Responsible AI objectives and measures", section: "enterprise_dependencies", outcome: "inherited_dependency", follow_up: "Confirm the enterprise provider, inheritance scope, required configuration, exclusions, evidence, and review period." },
    { control_id: "AI-GOV-008", title: "AI exceptions and residual-risk acceptance", section: "system_controls", outcome: "undetermined", follow_up: "Does this system require an exception, compensating control, or residual-risk acceptance?" },
    { control_id: "AI-GOV-009", title: "AI governance management review", section: "enterprise_dependencies", outcome: "inherited_dependency", follow_up: "Confirm the enterprise provider, inheritance scope, required configuration, exclusions, evidence, and review period." },
    { control_id: "AI-GOV-010", title: "AI concerns and adverse-impact reporting", section: "system_controls", outcome: "applicable", follow_up: "" },
    { control_id: "AI-USE-001", title: "Approved AI tools and configurations", section: "enterprise_dependencies", outcome: "inherited_dependency", follow_up: "Confirm the enterprise provider, inheritance scope, required configuration, exclusions, evidence, and review period." },
    { control_id: "AI-USE-002", title: "AI literacy and user awareness", section: "enterprise_dependencies", outcome: "inherited_dependency", follow_up: "Confirm the enterprise provider, inheritance scope, required configuration, exclusions, evidence, and review period." },
    { control_id: "AI-USE-003", title: "User verification of material AI outputs", section: "system_controls", outcome: If(
            Or(
                    Or(
                    Topic.decision_impact = "operational",
                    Topic.decision_impact = "consequential",
                    Topic.decision_impact = "regulated_or_consequential"
                ),
                    Or(
                    Topic.action_authority = "recommend",
                    Topic.action_authority = "modify_nonproduction",
                    Topic.action_authority = "modify_production",
                    Topic.action_authority = "execute_material_transaction",
                    Topic.action_authority = "safety_relevant_action"
                )
                ),
            "applicable",
            "undetermined"
        ), follow_up: "Could an incorrect output create more than negligible harm in the intended context?" },
    { control_id: "AI-USE-004", title: "Confidential and restricted information use boundaries", section: "enterprise_dependencies", outcome: "inherited_dependency", follow_up: "Confirm the enterprise provider, inheritance scope, required configuration, exclusions, evidence, and review period." },
    { control_id: "AI-INV-001", title: "AI discovery and inventory reconciliation", section: "enterprise_dependencies", outcome: "inherited_dependency", follow_up: "Confirm the enterprise provider, inheritance scope, required configuration, exclusions, evidence, and review period." },
    { control_id: "AI-INV-002", title: "AI resource and dependency documentation", section: "system_controls", outcome: "applicable", follow_up: "" },
    { control_id: "AI-INV-003", title: "AI lifecycle status and review", section: "system_controls", outcome: "applicable", follow_up: "" },
    { control_id: "AI-RSK-001", title: "AI regulatory role and applicability classification", section: "system_controls", outcome: "undetermined", follow_up: "Which legal, regulatory, contractual, or sector requirements apply to this system and the organization's role?" },
    { control_id: "AI-RSK-002", title: "AI impact assessment", section: "system_controls", outcome: If(
            Or(
                    Or(
                    Topic.decision_impact = "consequential",
                    Topic.decision_impact = "regulated_or_consequential"
                ),
                    Or(
                    Topic.external_reach = "bounded",
                    Topic.external_reach = "broad"
                )
                ),
            "applicable",
            "undetermined"
        ), follow_up: "Could the system materially affect individuals, employees, customers, or external parties?" },
    { control_id: "AI-RSK-003", title: "AI risk treatment and residual-risk approval", section: "system_controls", outcome: "applicable", follow_up: "" },
    { control_id: "AI-DAT-005", title: "AI data acquisition and rights", section: "system_controls", outcome: "undetermined", follow_up: "How was each material dataset acquired, and what rights or restrictions govern its AI use?" },
    { control_id: "AI-DAT-006", title: "AI data preparation and transformation", section: "system_controls", outcome: "undetermined", follow_up: "Is data prepared or transformed for training, evaluation, retrieval, grounding, or feedback?" },
    { control_id: "AI-DAT-007", title: "AI data quality and representativeness", section: "system_controls", outcome: "undetermined", follow_up: "Which data materially affects behavior or outcomes, and how are quality and representativeness evaluated?" },
    { control_id: "AI-DAT-008", title: "Retrieval and grounding governance", section: "system_controls", outcome: "undetermined", follow_up: "Does the system retrieve or ground responses in documents, knowledge stores, embeddings, or agent memory?" },
    { control_id: "AI-DAT-009", title: "Feedback and learning-data governance", section: "system_controls", outcome: "undetermined", follow_up: "Can user feedback, interactions, or telemetry change the system or be used for provider improvement?" },
    { control_id: "AI-MOD-001", title: "Model inventory and version control", section: "system_controls", outcome: "applicable", follow_up: "" },
    { control_id: "AI-MOD-002", title: "Model selection and approval", section: "system_controls", outcome: "applicable", follow_up: "" },
    { control_id: "AI-MOD-003", title: "Model and behavior-configuration change control", section: "system_controls", outcome: "undetermined", follow_up: "Which behavior-affecting components can change, and what change-control process applies?" },
    { control_id: "AI-MOD-004", title: "Model evaluation and acceptance thresholds", section: "system_controls", outcome: If(
            Or(
                    Or(
                    Topic.decision_impact = "operational",
                    Topic.decision_impact = "consequential",
                    Topic.decision_impact = "regulated_or_consequential"
                ),
                    Or(
                    Topic.action_authority = "recommend",
                    Topic.action_authority = "modify_nonproduction",
                    Topic.action_authority = "modify_production",
                    Topic.action_authority = "execute_material_transaction",
                    Topic.action_authority = "safety_relevant_action"
                )
                ),
            "applicable",
            "undetermined"
        ), follow_up: "Could model behavior materially affect system outcomes or control effectiveness?" },
    { control_id: "AI-PLT-001", title: "AI platform and tenant isolation", section: "system_controls", outcome: "undetermined", follow_up: "Does the system use a shared, hosted, multi-tenant, or multi-environment AI platform?" },
    { control_id: "AI-PLT-002", title: "AI platform privileged administration", section: "system_controls", outcome: If(
            Topic.system_access = "privileged",
            "applicable",
            "undetermined"
        ), follow_up: "Who can administer models, safety settings, data stores, gateways, tenants, or vendor support access?" },
    { control_id: "AI-PLT-003", title: "AI endpoint and gateway governance", section: "system_controls", outcome: If(
            Or(
                    Or(
                    Topic.external_reach = "bounded",
                    Topic.external_reach = "broad"
                ),
                    Or(
                    Topic.system_access = "standard",
                    Topic.system_access = "privileged"
                ),
                    "|external_tools|" in Topic.agent_capabilities_token
                ),
            "applicable",
            "undetermined"
        ), follow_up: "Does the system expose or consume model endpoints, gateways, brokers, or AI service APIs?" },
    { control_id: "AI-HUM-001", title: "Human oversight design and authority", section: "system_controls", outcome: If(
            Or(
                    Or(
                    Topic.autonomy_level = "autonomous",
                    Topic.autonomy_level = "conditionally_autonomous"
                ),
                    Or(
                    Topic.decision_impact = "consequential",
                    Topic.decision_impact = "regulated_or_consequential"
                ),
                    Or(
                    Topic.external_reach = "bounded",
                    Topic.external_reach = "broad"
                ),
                    Or(
                    Topic.action_authority = "modify_production",
                    Topic.action_authority = "execute_material_transaction",
                    Topic.action_authority = "safety_relevant_action"
                )
                ),
            "applicable",
            "undetermined"
        ), follow_up: "Do reviewers have sufficient information, time, competence, and authority to intervene effectively?" },
    { control_id: "AI-HUM-002", title: "Human decision accountability and contestability", section: "system_controls", outcome: If(
            Or(
                    Topic.decision_impact = "consequential",
                    Topic.decision_impact = "regulated_or_consequential"
                ),
            "applicable",
            "undetermined"
        ), follow_up: "Can an individual or customer be materially affected, and what review, appeal, or correction route is available?" },
    { control_id: "AI-HUM-003", title: "AI disclosure and user information", section: "system_controls", outcome: If(
            Or(
                    Or(
                    Topic.external_reach = "bounded",
                    Topic.external_reach = "broad"
                ),
                    Or(
                    Topic.decision_impact = "operational",
                    Topic.decision_impact = "consequential",
                    Topic.decision_impact = "regulated_or_consequential"
                )
                ),
            "applicable",
            "undetermined"
        ), follow_up: "Do users or affected parties need disclosure of AI interaction, generated content, limitations, or human responsibilities?" },
    { control_id: "AI-OPS-005", title: "Model, data, and retrieval drift monitoring", section: "system_controls", outcome: "undetermined", follow_up: "Which changing models, data, retrieval sources, providers, or contextual factors could materially affect outcomes?" },
    { control_id: "AI-OPS-006", title: "AI nonconformity and corrective action", section: "system_controls", outcome: "applicable", follow_up: "" },
    { control_id: "AI-VSC-006", title: "Vendor customer-data training restrictions", section: "system_controls", outcome: "undetermined", follow_up: "Does a third party receive non-public data, and can it use prompts, outputs, telemetry, or artifacts for training or improvement?" },
    { control_id: "AI-VSC-007", title: "Vendor AI artifact deletion and return", section: "system_controls", outcome: "undetermined", follow_up: "Can a supplier store or derive prompts, outputs, embeddings, fine-tunes, memory, logs, or other artifacts from organizational data?" },
    { control_id: "AI-VSC-008", title: "Vendor AI incident notification and cooperation", section: "system_controls", outcome: "undetermined", follow_up: "Which material AI suppliers require defined incident notification, evidence preservation, cooperation, and remediation obligations?" },
    { control_id: "AI-VSC-009", title: "Vendor AI assurance and audit rights", section: "system_controls", outcome: "undetermined", follow_up: "Could supplier failure create material impact, and what independent assurance, evidence, or audit rights are available?" }
)
