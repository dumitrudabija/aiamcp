"""
Capability Evidence Packs

Exactly four evidence checklists (per spec - client/regulated impact is
intentionally NOT a fifth pack; it stays within the existing 47 questions
and governance escalation logic) that identify additional evidence needed
around specific model capabilities: knowledge retrieval, tool/action
execution, autonomous operation, and vendor/platform delivery.

Key design principle: Capability Evidence Packs do NOT produce independent
risk scores. They trigger deterministically off the verified/unverified
status of the model_type_classification promotion gates (see
model_type_classification.py) plus the delivery_model label, and produce
evidence gaps, conditions, blockers, and governance actions - never a score.
Every finding is mapped back to one or more of the existing 8 OSFI E-23 risk
dimensions; no new risk vocabulary is introduced.
"""

from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


def _gate_verified(model_type_classification: Dict[str, Any], gate_name: str) -> bool:
    return bool(
        model_type_classification.get("promotion_gates", {}).get(gate_name, {}).get("verified")
    )


def _is_yes(evidence: Dict[str, Any], field_id: str) -> bool:
    return evidence.get(field_id) == "yes"


def _kq(question_id: str, question: str, expected_evidence_or_control: str,
        condition_if_missing: str, blocker_if_missing: bool, blocker_reason: str) -> Dict[str, Any]:
    """
    Build one static Key Question reference entry. These are NOT extracted
    from the project description or verified by this tool - the evidence for
    these external/operational controls (vendor contracts, audit rights,
    tested kill switches, etc.) would never appear in a project description.
    They are rendered as a fixed reference/follow-up checklist under each
    triggered pack, for the institution to confirm internally.
    `blocker_if_missing` is the spec's stated DEFAULT for this question;
    `blocker_reason` states the full condition under which it applies -
    read together as guidance, not a computed determination.
    """
    return {
        "question_id": question_id,
        "question": question,
        "expected_evidence_or_control": expected_evidence_or_control,
        "evidence_status": "not_verified",
        "evidence_summary": "Not assessed by this tool - verify with the accountable control owner.",
        "missing_evidence": "This is an external/operational control not evidenced in the project description.",
        "condition_if_missing": condition_if_missing,
        "blocker_if_missing": blocker_if_missing,
        "blocker_reason": blocker_reason,
    }


# =============================================================================
# PACK 1: KNOWLEDGE ACCESS PACK
# =============================================================================

def _knowledge_access_trigger(model_type_classification, delivery_model, evidence) -> Dict[str, Any]:
    triggered = _gate_verified(model_type_classification, "runtime_retrieval")
    reasons = ["runtime_retrieval.verified=true"] if triggered else []
    return {"triggered": triggered, "reasons": reasons}


def _knowledge_access_result(evidence: Dict[str, Any]) -> Dict[str, Any]:
    findings = [
        "The system retrieves from internal or external knowledge sources at runtime (e.g. enterprise "
        "search, RAG, vector search/embeddings, SharePoint, Confluence, CRM, email, databases, policy "
        "documents, PDFs, websites, knowledge bases), which introduces retrieval-quality, access-control, "
        "and data-governance risk beyond the underlying model itself."
    ]
    conditions = [
        "Confirm a process exists to keep retrieval indexes/sources current and remove stale or incorrect content.",
    ]
    priorities = ["medium"]
    evidence_gaps = []
    if not _is_yes(evidence, "has_retrieval_access_controls"):
        evidence_gaps.append("Retrieval source access-control/entitlement not confirmed.")
        conditions.append("Confirm retrieved sources are authorized for this use case and access-controlled/entitled appropriately.")
        priorities.append("high")
    governance_actions = [
        {"category": "Security / access controls", "action": c, "priority": p}
        for c, p in zip(conditions, priorities)
    ]
    return {
        "findings": findings,
        "evidence_gaps": evidence_gaps,
        "conditions": conditions,
        "blockers": [],
        "governance_actions": governance_actions,
    }


KA_KEY_QUESTIONS = [
    _kq("KA-01", "Are all runtime knowledge sources identified and approved?",
        "Documented source inventory including source name, owner, system of record, data classification, approved use, and business purpose.",
        "Document and approve all runtime knowledge sources before production.", True,
        "True if the system uses production, customer, confidential, regulated, or decision-critical knowledge sources."),
    _kq("KA-02", "Is each knowledge source assigned to an accountable business or data owner?",
        "Named owner for each source with responsibility for quality, access, approval, and change notification.",
        "Assign accountable owners for all runtime knowledge sources.", False,
        "False by default; true if ownerless sources are used for customer-facing, regulated, or high-impact outputs."),
    _kq("KA-03", "Does retrieval enforce user, role, purpose, and source-level entitlements?",
        "Access-control design, entitlement mapping, test results, and evidence that retrieval cannot expose documents the user or model context is not authorized to access.",
        "Implement and test entitlement enforcement for runtime retrieval.", True,
        "True when retrieval may access confidential, customer, employee, regulated, or commercially sensitive information."),
    _kq("KA-04", "Are retrieved sources classified by sensitivity and permitted use?",
        "Data classification labels, permitted-use documentation, restrictions for confidential or regulated information, and handling rules.",
        "Classify all retrieved sources and document permitted-use constraints.", True,
        "True if classification is absent for sensitive or regulated data."),
    _kq("KA-05", "Are freshness requirements, indexing frequency, and stale-content controls defined?",
        "Indexing schedule, freshness SLA, stale-content detection, source update process, and re-indexing controls.",
        "Define freshness requirements and controls for retrieved content.", True,
        "True if stale content could materially affect customer, financial, legal, regulatory, or operational decisions."),
    _kq("KA-06", "Has retrieval quality been tested for relevance, completeness, and source accuracy?",
        "Retrieval evaluation results, test queries, relevance benchmarks, false positive/false negative analysis, and remediation plan.",
        "Perform retrieval quality testing before production.", True,
        "True for customer-facing, regulated, or decision-support use cases."),
    _kq("KA-07", "Can generated outputs be traced back to retrieved sources?",
        "Source citation design, retrieval logs, source snippets or document references, and audit trail connecting output to source evidence.",
        "Enable traceability from output to retrieved source evidence.", True,
        "True if outputs are used for regulated decisions, customer advice, legal/compliance interpretation, or audit-sensitive processes."),
    _kq("KA-08", "Are controls in place to prevent malicious or inappropriate retrieved content from manipulating the model?",
        "Prompt-injection testing, content filtering, source trust rules, instruction hierarchy, retrieval sanitization, and red-team results.",
        "Test and implement controls against retrieval-based prompt injection and source manipulation.", True,
        "True if retrieval includes external, user-generated, web, email, chat, ticket, or other untrusted content."),
    _kq("KA-09", "Are there controls to prevent retrieved sensitive data from being exposed in outputs?",
        "PII/PCI/PHI/confidential data filtering, output guardrails, retention controls, masking, leakage testing, and audit logs.",
        "Implement sensitive data leakage controls for retrieved content.", True,
        "True when retrieval may access sensitive, regulated, or confidential data."),
    _kq("KA-10", "Are retrieval requests, sources accessed, outputs, and errors logged and monitored?",
        "Retrieval logs, access logs, monitoring dashboards, anomaly detection, error handling, and retention policy.",
        "Enable retrieval logging and monitoring before production.", True,
        "True for production systems with customer, regulated, sensitive, or high-impact use."),
    _kq("KA-11", "Does the system depend on a single critical knowledge source, search index, vector database, or retrieval provider?",
        "Dependency inventory, resilience design, failover, degradation behavior, and substitution plan.",
        "Document retrieval dependencies and resilience plan.", True,
        "True if outage or corruption of the source/index would stop or materially impair a critical business process."),
    _kq("KA-12", "Are source onboarding, change, retirement, and deletion processes defined?",
        "Source onboarding checklist, change management, deletion propagation, re-indexing process, and owner approval.",
        "Define lifecycle controls for runtime knowledge sources.", False,
        "False by default; true when deletion or change failures could create legal, privacy, or regulatory exposure."),
]


PACK_KNOWLEDGE_ACCESS = {
    "pack_id": "knowledge_access",
    "pack_name": "Knowledge Access Pack",
    "key_questions": KA_KEY_QUESTIONS,
    "mapped_dimensions": ["output_reliability", "operational_security", "governance_oversight", "data_provenance_supply_chain", "systemic_concentration_risk"],
    "risk_dimension_mapping_notes": (
        "Runtime retrieval affects Output Reliability (grounding/citation quality), Operational & Security "
        "Risk (access control, injection), Governance & Oversight (monitoring, ownership), Data Provenance & "
        "Supply Chain Risk (source quality/classification), and Systemic & Concentration Risk (dependency on "
        "a single index/provider)."
    ),
    "trigger_fn": _knowledge_access_trigger,
    "result_fn": _knowledge_access_result,
    "not_triggered_reason": "runtime_retrieval is not verified - the system does not retrieve from knowledge sources at runtime.",
}


# =============================================================================
# PACK 2: ACTION EXECUTION PACK
# =============================================================================

def _action_execution_trigger(model_type_classification, delivery_model, evidence) -> Dict[str, Any]:
    triggered = _gate_verified(model_type_classification, "tool_or_action_execution")
    reasons = ["tool_or_action_execution.verified=true"] if triggered else []
    return {"triggered": triggered, "reasons": reasons}


def _action_execution_result(evidence: Dict[str, Any]) -> Dict[str, Any]:
    findings = [
        "The system can take actions (calling APIs, writing records, creating tickets, routing work, "
        "sending messages, approving items, executing transactions, or otherwise changing system state) "
        "rather than only producing text, which introduces operational and change-control risk."
    ]
    conditions = [
        "Confirm each action type is explicitly authorized and scoped (least-privilege).",
        "Confirm a rollback or compensating-action process exists for erroneous actions.",
    ]
    priorities = ["high", "high"]
    evidence_gaps = []
    blockers = []
    if not _is_yes(evidence, "has_action_audit_logging"):
        evidence_gaps.append("Action-level audit logging not confirmed.")
        conditions.append("Enable action-level audit logging before production.")
        priorities.append("blocker")
        blockers.append("Action-level audit logging not confirmed - production blocker until resolved.")
    governance_actions = [
        {"category": "Monitoring", "action": c, "priority": p} for c, p in zip(conditions, priorities)
    ]
    return {
        "findings": findings,
        "evidence_gaps": evidence_gaps,
        "conditions": conditions,
        "blockers": blockers,
        "governance_actions": governance_actions,
    }


AE_KEY_QUESTIONS = [
    _kq("AE-01", "Are all possible model- or AI-triggered actions identified?",
        "Action catalog listing every tool, API, workflow, record write, transaction, message, approval, routing action, and downstream system change.",
        "Document a complete action inventory before production.", True,
        "True for production systems that can write records, approve items, execute transactions, send customer communications, or change customer/account status."),
    _kq("AE-02", "Is each action explicitly authorized and scoped to least privilege?",
        "Permission model, service-account design, role mapping, API scopes, environment restrictions, and least-privilege review.",
        "Confirm each action type is explicitly authorized and scoped using least privilege.", True,
        "True if the system can write records, execute transactions, send communications, or access sensitive systems."),
    _kq("AE-03", "Are the conditions under which each action can occur defined and testable?",
        "Decision rules, thresholds, model-output mapping, trigger logic, policy constraints, and test cases.",
        "Define and test trigger criteria for each action.", True,
        "True if action triggers affect customers, financial exposure, regulatory reporting, or system-of-record state."),
    _kq("AE-04", "Which actions require human approval before execution?",
        "Approval matrix by action type, risk level, dollar value, customer impact, confidence threshold, and exception category.",
        "Define human approval gates for high-impact or high-risk actions.", True,
        "True if high-impact actions can execute without documented approval criteria."),
    _kq("AE-05", "Are all actions logged with who/what/when/why/context/result?",
        "Action logs capturing model version, input reference, output, action selected, actor/service account, timestamp, target system, result, errors, override, and correlation ID.",
        "Enable action-level audit logging before production.", True,
        "True for all production action-executing systems."),
    _kq("AE-06", "Can erroneous actions be reversed, corrected, or compensated?",
        "Rollback process, compensating controls, correction workflow, customer remediation process, owner, SLA, and tested runbook.",
        "Confirm a rollback or compensating-action process exists for erroneous actions.", True,
        "True if actions materially affect customers, accounts, financial exposure, regulatory obligations, or operational resilience."),
    _kq("AE-07", "Are controls in place to prevent duplicate or repeated unintended actions?",
        "Idempotency keys, duplicate detection, retry controls, transaction boundaries, rate limits, and reconciliation checks.",
        "Implement controls to prevent duplicate or unintended repeated actions.", True,
        "True if repeated actions could create customer harm, financial loss, operational disruption, or compliance exposure."),
    _kq("AE-08", "Are development, approval, execution, and monitoring responsibilities appropriately separated?",
        "RACI, access controls, release approvals, production permissions, monitoring ownership, and independent review.",
        "Establish segregation of duties for action-executing capabilities.", False,
        "False by default; true for critical/high-impact production actions with no independent approval or monitoring."),
    _kq("AE-09", "Have downstream systems validated expected input format, ranges, and failure handling?",
        "Interface specifications, contract tests, API validation, schema validation, error handling, and integration test results.",
        "Validate downstream system interfaces and failure handling before production.", True,
        "True if malformed or unexpected outputs could create incorrect records, transactions, customer communications, or operational outages."),
    _kq("AE-10", "Are actions monitored for volume, failure rate, exception rate, unusual patterns, and policy breaches?",
        "Monitoring dashboards, thresholds, alerts, exception queues, anomaly detection, owner, and escalation path.",
        "Implement action monitoring and alerting before production.", True,
        "True for production systems that execute customer, financial, regulated, or operationally material actions."),
    _kq("AE-11", "Are actions that affect customers, disclosures, eligibility, pricing, credit, or access subject to additional controls?",
        "Customer impact assessment, fairness review, adverse-action handling, complaint process, disclosure review, regulatory mapping, and legal/compliance sign-off.",
        "Complete customer and regulatory impact controls for material actions.", True,
        "True if the action affects customer outcomes, credit, eligibility, pricing, access to products, legal rights, or regulatory obligations."),
    _kq("AE-12", "Can action execution be quickly disabled without shutting down unrelated systems?",
        "Feature flag, action kill switch, permission revocation, circuit breaker, operational runbook, tested disablement procedure.",
        "Implement an emergency disablement mechanism for action execution.", True,
        "True for production systems that can materially change system state or customer outcomes."),
]


PACK_ACTION_EXECUTION = {
    "pack_id": "action_execution",
    "key_questions": AE_KEY_QUESTIONS,
    "pack_name": "Action Execution Pack",
    "mapped_dimensions": ["misuse_unintended_harm", "operational_security", "complexity_opacity", "governance_oversight", "data_provenance_supply_chain"],
    "risk_dimension_mapping_notes": (
        "Action execution affects Misuse & Unintended Harm Potential (erroneous/unintended actions), "
        "Operational & Security Risk (authorization, rollback), Model Complexity & Opacity (traceability of "
        "which action was taken and why), Governance & Oversight (approval gates, segregation of duties), "
        "and Data Provenance & Supply Chain Risk (downstream system/interface integrity)."
    ),
    "trigger_fn": _action_execution_trigger,
    "result_fn": _action_execution_result,
    "not_triggered_reason": "tool_or_action_execution is not verified - the system cannot select/invoke tools, APIs, or actions.",
}


# =============================================================================
# PACK 3: AUTONOMY PACK
# =============================================================================

def _autonomy_trigger(model_type_classification, delivery_model, evidence) -> Dict[str, Any]:
    triggered = _gate_verified(model_type_classification, "autonomous_operation")
    reasons = ["autonomous_operation.verified=true"] if triggered else []
    return {"triggered": triggered, "reasons": reasons}


def _autonomy_result(evidence: Dict[str, Any], model_type_classification: Dict[str, Any]) -> Dict[str, Any]:
    findings = [
        "The system exhibits autonomous behavior (event triggers, scheduled execution, goal pursuit, "
        "multi-step planning, chaining, loops, retries, delegation, memory/state, or escalation without "
        "approval at every step), which introduces risk of unintended or compounding actions."
    ]
    if not _gate_verified(model_type_classification, "tool_or_action_execution"):
        findings.append(
            "Note: autonomous behavior was detected without verified tool/action execution capability - "
            "per the classification rules this is an evidence gap and does not by itself promote the "
            "model to Level 5 (Autonomous agent); confirm whether action capability exists but was "
            "simply not described."
        )

    conditions = [
        "Confirm monitoring is in place to detect the system operating outside its intended scope.",
        "Confirm governance approval accounts for the autonomy level, not just the underlying model's accuracy.",
    ]
    priorities = ["high", "high"]
    evidence_gaps = []
    blockers = []
    if not _is_yes(evidence, "has_kill_switch_or_stop_condition"):
        evidence_gaps.append("Kill-switch/stop-condition capability not confirmed.")
        conditions.append("Implement and test a kill-switch/stop condition before production.")
        priorities.append("blocker")
        blockers.append("No verified ability to halt the autonomous process - production blocker until resolved.")
    governance_actions = [
        {"category": "Human oversight", "action": c, "priority": p} for c, p in zip(conditions, priorities)
    ]
    return {
        "findings": findings,
        "evidence_gaps": evidence_gaps,
        "conditions": conditions,
        "blockers": blockers,
        "governance_actions": governance_actions,
    }


AU_KEY_QUESTIONS = [
    _kq("AU-01", "Is the autonomous agent's goal, task scope, and prohibited scope clearly defined?",
        "Agent goal statement, allowed tasks, prohibited tasks, policy boundaries, use-case scope, and examples of out-of-scope requests.",
        "Define the agent's goal, allowed scope, and prohibited scope before production.", True,
        "True for all production autonomous agents."),
    _kq("AU-02", "Is it clear when the AI is allowed to decide to act or continue?",
        "Decision-to-act criteria, continuation criteria, stopping rules, confidence thresholds, human escalation rules, and examples.",
        "Define when the agent may act, continue, stop, or escalate.", True,
        "True for all production autonomous agents."),
    _kq("AU-03", "Are the actions/tools available to the agent explicitly bounded?",
        "Tool registry, action whitelist, permission scopes, blocked actions, environment restrictions, and least-privilege configuration.",
        "Explicitly bound the agent's tools and actions.", True,
        "True for all production autonomous agents."),
    _kq("AU-04", "Can the agent's plan, intermediate steps, tool calls, and decisions be reconstructed?",
        "Agent trace logs, chain-of-thought-safe reasoning summaries, tool-call logs, decision records, observations, plan revisions, and correlation IDs.",
        "Enable traceability for autonomous decisions, steps, and tool calls.", True,
        "True for all production autonomous agents."),
    _kq("AU-05", "Can the autonomous process be halted quickly and reliably?",
        "Kill switch, stop condition, circuit breaker, manual override, tested runbook, owner, and operational SLA.",
        "Implement and test a kill-switch or stop condition before production.", True,
        "True for all production autonomous agents."),
    _kq("AU-06", "Are loops, retries, timeouts, and escalation paths bounded?",
        "Maximum retries, timeouts, loop controls, escalation thresholds, failure handling, and monitoring alerts.",
        "Define and enforce loop, retry, timeout, and escalation limits.", True,
        "True if the agent can loop, retry, escalate, or continue without human approval."),
    _kq("AU-07", "What human oversight applies before, during, and after autonomous operation?",
        "Human-in-the-loop, human-on-the-loop, sampling review, exception review, approval matrix, and escalation model.",
        "Define the human oversight model for autonomous operation.", True,
        "True for customer-impacting, regulated, financial, or operationally critical autonomous agents."),
    _kq("AU-08", "Have guardrails been tested against misuse, unsafe actions, prompt injection, and out-of-scope tasks?",
        "Red-team tests, adversarial tests, misuse scenarios, tool-abuse tests, prompt-injection tests, and remediation results.",
        "Complete guardrail and adversarial testing for autonomous behavior.", True,
        "True for exposed, customer-facing, vendor-connected, action-executing, or sensitive-data agents."),
    _kq("AU-09", "If the agent uses memory or state, are retention, privacy, reset, and contamination controls defined?",
        "Memory design, retained fields, retention period, deletion process, privacy assessment, memory reset controls, and contamination testing.",
        "Define memory/state controls for autonomous operation.", True,
        "True if memory contains customer, employee, confidential, regulated, or decision-relevant information."),
    _kq("AU-10", "Is monitoring in place to detect the agent operating outside intended scope?",
        "Behavior monitoring, action monitoring, out-of-scope detection, anomaly alerts, escalation triggers, and owner.",
        "Confirm monitoring is in place to detect autonomous operation outside intended scope.", True,
        "True for all production autonomous agents."),
    _kq("AU-11", "If the agent delegates to other agents or subprocesses, are delegation boundaries and accountability defined?",
        "Delegation map, sub-agent roles, handoff rules, permission inheritance, accountability model, traceability, and failure handling.",
        "Define delegation controls for multi-agent or subprocess workflows.", True,
        "True if delegation occurs without traceability, bounded authority, or accountable ownership."),
    _kq("AU-12", "Has governance approval explicitly considered the autonomy level, not just model accuracy?",
        "Approval record showing review of autonomy, tool authority, goal boundaries, stop controls, monitoring, and residual risk.",
        "Confirm governance approval accounts for autonomy level, not just model performance.", True,
        "True before production for all autonomous agents."),
]


PACK_AUTONOMY = {
    "pack_id": "autonomy",
    "pack_name": "Autonomy Pack",
    "key_questions": AU_KEY_QUESTIONS,
    "mapped_dimensions": ["misuse_unintended_harm", "operational_security", "complexity_opacity", "governance_oversight", "systemic_concentration_risk"],
    "risk_dimension_mapping_notes": (
        "Autonomous operation affects Misuse & Unintended Harm Potential (compounding/unintended actions), "
        "Operational & Security Risk (loop/retry/escalation controls), Model Complexity & Opacity "
        "(plan/step traceability), Governance & Oversight (human oversight model, autonomy-specific "
        "approval), and Systemic & Concentration Risk (delegation to other agents/subprocesses)."
    ),
    "trigger_fn": _autonomy_trigger,
    "result_fn": _autonomy_result,  # needs model_type_classification too - special-cased below
    "not_triggered_reason": "autonomous_operation is not verified - the system does not operate autonomously (trigger/schedule-based, looping, delegating) without per-step approval.",
}


# =============================================================================
# PACK 4: VENDOR / PLATFORM PACK
# =============================================================================

_VENDOR_EVIDENCE_TRIGGER_FIELDS = [
    "vendor_controls_model_runtime", "vendor_controls_model_updates",
    "vendor_hosts_customer_or_sensitive_data", "vendor_provides_foundation_model_or_agent_platform",
]


def _vendor_platform_trigger(model_type_classification, delivery_model, evidence) -> Dict[str, Any]:
    label = delivery_model.get("label")
    label_triggered = label in ("vendor_platform", "embedded_saas_ai")
    evidence_fields_triggered = [f for f in _VENDOR_EVIDENCE_TRIGGER_FIELDS if _is_yes(evidence, f)]
    triggered = label_triggered or bool(evidence_fields_triggered)

    reasons = []
    if label_triggered:
        reasons.append(f"delivery_model.label={label}")
    reasons.extend(f"{f}=yes" for f in evidence_fields_triggered)
    return {"triggered": triggered, "reasons": reasons}


def _vendor_platform_result(evidence: Dict[str, Any]) -> Dict[str, Any]:
    findings = [
        "The AI capability is provided or hosted by a third-party vendor/platform (e.g. Agentforce, "
        "ServiceNow AI Agents / Now Assist, Microsoft Copilot, or other vendor-hosted/SaaS AI), which "
        "introduces vendor-management, data-residency, and shared-fate operational risk."
    ]
    conditions = [
        "Confirm the institution can assess and respond to vendor-initiated model/agent/tool updates.",
    ]
    priorities = ["medium"]
    evidence_gaps = []
    if not _is_yes(evidence, "has_vendor_assurance_evidence"):
        evidence_gaps.append("Vendor assurance evidence (audit rights/incident notification/compliance report) not confirmed.")
        conditions.append("Obtain vendor assurance evidence (contractual right-to-audit, incident notification terms, compliance report) before production.")
        priorities.append("high")
    governance_actions = [
        {"category": "Vendor assurance", "action": c, "priority": p} for c, p in zip(conditions, priorities)
    ]
    return {
        "findings": findings,
        "evidence_gaps": evidence_gaps,
        "conditions": conditions,
        "blockers": [],
        "governance_actions": governance_actions,
    }


VP_KEY_QUESTIONS = [
    _kq("VP-01", "Are all vendors, platforms, embedded AI services, and third-party components identified?",
        "Vendor inventory, service description, component list, architecture diagram, data flow, subcontractor list, and business owner.",
        "Document all vendor/platform dependencies and owners.", True,
        "True if vendor components process sensitive data, support material decisions, or affect critical operations."),
    _kq("VP-02", "Is the control split between the institution and vendor clearly defined?",
        "Shared responsibility model, RACI, contract controls, control matrix, and operational ownership.",
        "Define institution/vendor control responsibilities.", True,
        "True if material controls are unassigned or assumed to be vendor-owned without evidence."),
    _kq("VP-03", "Has vendor risk, security, privacy, compliance, and model governance due diligence been completed?",
        "Vendor risk assessment, security review, privacy review, compliance review, model/AI governance review, and approval record.",
        "Complete vendor due diligence before production.", True,
        "True for material, customer-impacting, sensitive-data, regulated, or critical-use vendors."),
    _kq("VP-04", "Are data residency, permitted use, retention, and training/fine-tuning restrictions defined?",
        "Contract clauses, data processing terms, residency documentation, retention terms, no-training commitments, deletion rights, and privacy assessment.",
        "Document vendor data residency, use, retention, and training restrictions.", True,
        "True when customer, employee, confidential, regulated, or proprietary data is processed by the vendor."),
    _kq("VP-05", "Does the institution have sufficient transparency into the model, platform, limitations, and changes?",
        "Model cards, system cards, release notes, limitations, validation evidence, API documentation, known issues, and vendor assurance materials.",
        "Obtain sufficient model/platform transparency evidence from the vendor.", True,
        "True if opaque vendor behavior materially affects regulated, customer, financial, or critical operational outcomes."),
    _kq("VP-06", "Are vendor model, prompt, policy, connector, or platform changes controlled and reviewable?",
        "Change notification terms, release notes, versioning, testing window, rollback process, configuration lock, and approval process.",
        "Establish vendor change notification, testing, and approval controls.", True,
        "True if silent or uncontrolled vendor changes could materially alter outputs, actions, security posture, or customer outcomes."),
    _kq("VP-07", "Can the institution obtain logs, evidence, reports, and audit support from the vendor?",
        "Audit rights, log access, SOC reports, compliance reports, incident records, export capabilities, and regulator support terms.",
        "Confirm audit rights and evidence access with the vendor.", True,
        "True if the institution cannot evidence controls for regulated, material, customer-impacting, or critical use."),
    _kq("VP-08", "Are service availability, continuity, substitutability, and exit plans defined?",
        "SLA, RTO/RPO, business continuity plan, failover, degradation mode, substitution plan, data export, and exit plan.",
        "Document resilience, continuity, and exit strategy for vendor dependency.", True,
        "True if vendor outage would stop or materially impair a critical business process."),
    _kq("VP-09", "Are vendor incident notification, investigation, and remediation obligations defined?",
        "Incident notification SLA, escalation contacts, support model, root-cause reporting, remediation commitments, and regulator-facing support.",
        "Define vendor incident notification and support obligations.", True,
        "True for sensitive-data, customer-impacting, regulated, or critical operations."),
    _kq("VP-10", "Are vendor platform access controls, authentication, authorization, and privileged access controls verified?",
        "SSO/MFA, RBAC, privileged access review, service accounts, key management, network controls, security testing, and vulnerability management evidence.",
        "Verify vendor platform security and access controls.", True,
        "True when vendor platform connects to enterprise systems, processes sensitive data, or can trigger actions."),
    _kq("VP-11", "Are material subcontractors, sub-processors, foundation model providers, data providers, and hosting dependencies understood?",
        "Subcontractor/sub-processor list, dependency map, flow-down obligations, concentration analysis, and notification rights.",
        "Document material subcontractors and dependency chain.", True,
        "True if unknown subcontractors process sensitive data or support critical/model-significant functionality."),
    _kq("VP-12", "Does the vendor/platform create concentration risk across the model or AI portfolio?",
        "Portfolio dependency analysis, shared foundation model/platform inventory, concentration thresholds, contingency plan, and executive reporting.",
        "Assess vendor/platform concentration risk across the portfolio.", False,
        "False at single-use-case level by default; true if a critical function depends on a non-substitutable vendor with no contingency plan."),
]


PACK_VENDOR_PLATFORM = {
    "pack_id": "vendor_platform",
    "pack_name": "Vendor / Platform Pack",
    "key_questions": VP_KEY_QUESTIONS,
    "mapped_dimensions": ["operational_security", "governance_oversight", "data_provenance_supply_chain", "systemic_concentration_risk", "output_reliability"],
    "risk_dimension_mapping_notes": (
        "Vendor/platform dependency affects Operational & Security Risk (access controls, resilience), "
        "Governance & Oversight (control-split, due diligence, change management), Data Provenance & Supply "
        "Chain Risk (subcontractors, data residency/use), Systemic & Concentration Risk (portfolio-level "
        "vendor concentration), and Output Reliability & Integrity (model/platform transparency)."
    ),
    "trigger_fn": _vendor_platform_trigger,
    "result_fn": _vendor_platform_result,
    "not_triggered_reason": "delivery_model is not vendor_platform or embedded_saas_ai, and no vendor-control/vendor-hosting evidence was stated.",
}


ALL_CAPABILITY_EVIDENCE_PACKS = [
    PACK_KNOWLEDGE_ACCESS,
    PACK_ACTION_EXECUTION,
    PACK_AUTONOMY,
    PACK_VENDOR_PLATFORM,
]


def evaluate_capability_evidence_packs(
    model_type_classification: Dict[str, Any],
    delivery_model: Dict[str, Any],
    evidence: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Evaluate all 4 Capability Evidence Packs against the classified model
    type (its promotion_gates), delivery_model, and structured evidence
    answers. Returns (triggered, not_triggered).

    Triggered packs include findings/evidence_gaps/governance_conditions/
    blockers/governance_actions/required_actions (all derived deterministically
    from real evidence - has_action_audit_logging, has_kill_switch_or_stop_condition,
    etc.), plus a static key_questions reference checklist (NOT extracted or
    verified against the project description - these are external/operational
    controls for the institution to confirm internally, rendered only when the
    pack triggers) and risk_dimension_mapping_notes. Not-triggered packs are
    recorded with a reason for auditability.
    """
    triggered_packs: List[Dict[str, Any]] = []
    not_triggered_packs: List[Dict[str, Any]] = []

    for pack in ALL_CAPABILITY_EVIDENCE_PACKS:
        trigger_result = pack["trigger_fn"](model_type_classification, delivery_model, evidence)

        if not trigger_result["triggered"]:
            not_triggered_packs.append({
                "pack_id": pack["pack_id"],
                "pack_name": pack["pack_name"],
                "triggered": False,
                "reason": pack["not_triggered_reason"],
            })
            continue

        if pack["pack_id"] == "autonomy":
            pack_result = pack["result_fn"](evidence, model_type_classification)
        else:
            pack_result = pack["result_fn"](evidence)

        governance_actions = pack_result["governance_actions"]

        triggered_packs.append({
            "pack_id": pack["pack_id"],
            "pack_name": pack["pack_name"],
            "triggered": True,
            "trigger_reason": "Triggered because: " + "; ".join(trigger_result["reasons"]),
            "mapped_dimensions": list(pack["mapped_dimensions"]),
            "risk_dimension_mapping_notes": pack.get("risk_dimension_mapping_notes", ""),
            "checks": trigger_result["reasons"],
            "key_questions": pack["key_questions"],
            "findings": pack_result["findings"],
            "evidence_gaps": pack_result["evidence_gaps"],
            "governance_conditions": pack_result["conditions"],
            "blockers": pack_result["blockers"],
            "governance_actions": governance_actions,
            "required_actions": [ga["action"] for ga in governance_actions],
        })

    return triggered_packs, not_triggered_packs


# Backward-compatible aliases (prior names used before this revision).
def evaluate_evidence_packs(model_type_classification, delivery_model, evidence):
    triggered, _ = evaluate_capability_evidence_packs(model_type_classification, delivery_model, evidence)
    return triggered


evaluate_conditional_modules = evaluate_evidence_packs
