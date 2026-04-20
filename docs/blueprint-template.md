# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: 
- [REPO_URL]: 
- [MEMBERS]:
  - Member A: Dương | Role: Logging & PII
  - Member B: Chung | Role: Tracing & Enrichment
  - Member C: Hoàng Anh | Role: SLO & Alerts
  - Member D: Đạt | Role: Load Test & Dashboard
  - Member E: Quân |Role: dashboard + evidence
  - Member F: Hiệp | Role: Demo & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: (Pending Member B)
- [PII_LEAKS_FOUND]: 0 

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: [Path to image]
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: [Path to image]
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: [Path to image]
- [TRACE_WATERFALL_EXPLANATION]: (Briefly explain one interesting span in your trace)

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: [Path to image]
- [SLO_TABLE]:
| SLI         |     Target | Window | Current Value |
| ----------- | ---------: | ------ | ------------: |
| Latency P95 |   < 3000ms | 28d    |               |
| Error Rate  |       < 2% | 28d    |               |
| Cost Budget | < $2.5/day | 1d     |               |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: [Path to image]
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md#L...]

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: End-to-end latency increased from ~813ms to ~1100ms (+37%) when rag_slow incident enabled. All requests still succeed (HTTP 200).
- [ROOT_CAUSE_PROVED_BY]: Log records show latency_ms=150 at API layer unchanged, indicating slowdown in agent.retrieve() or mock_rag stage. Verified by enabling/disabling incident scenario and re-running load tests.
- [FIX_ACTION]: Disabled rag_slow incident. Latency returned to baseline ~803ms.
- [PREVENTIVE_MEASURE]: Set timeout threshold for RAG retrieval stage; trigger P2 alert if P95 latency exceeds 5000ms for 30m window (see config/alert_rules.yaml). 

---

## 5. Individual Contributions & Evidence

### [MEMBER_A_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: (Link to specific commit or PR)

### [MEMBER_B_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### [MEMBER_C_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### [MEMBER_D_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### [MEMBER_E_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
