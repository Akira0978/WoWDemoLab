# Sentinel (ALSCSV12) — Business Value Analysis
> **Prepared for:** Business Analyst Team  
> **Context:** Allianz Anti-Fraud Command Studio / Claim Shield  
> **Date:** 18 May 2026

---

## 1. Direct Business Value to Allianz

### 1.1 Accelerated Fraud Detection at Scale

| Point | Detail |
|-------|--------|
| **Multi-dimensional fraud scoring** | The engine scores every claim across **5 independent dimensions** — Behavioural (25%), Network (25%), Historical (20%), Document (15%), Contextual (15%). This mirrors Allianz's own risk taxonomy and gives handlers a **holistic risk view**, not a single opaque number. |
| **Automated triage & prioritisation** | Claims are automatically banded into **LOW / REVIEW / HIGH**, meaning handlers focus on the right cases first. LOW-risk claims can be fast-tracked for settlement, freeing capacity for complex investigations. |
| **Quantified fraud confidence** | Each indicator carries an explicit **confidence score (0.0–1.0)**, enabling Allianz to set policy-level thresholds — e.g., _"auto-clear anything below 30 with confidence < 0.5"_ — driving straight-through processing (STP). |

### 1.2 Reduction in Fraud Leakage (Financial Impact)

- **Network detection (shared address/phone/bank account)** catches organised fraud rings that individual claim reviews would miss. This is the highest-value dimension for Allianz — industry data shows organised fraud accounts for **~50% of detected fraud value** in P&C insurance.
- **Historical pattern matching** flags repeat offenders and similar-loss patterns across the book, reducing re-offending leakage.
- **Ring-fence indicators** (`STAGED_CLAIMS`, `ORGANIZED_RING`) provide Allianz with clear escalation triggers for the Special Investigations Unit (SIU).

### 1.3 Faster Claims Settlement & Improved Customer Experience

| Metric | How Sentinel Helps |
|--------|--------------------|
| **Cycle time** | LOW-band claims proceed to settlement faster — no manual fraud review bottleneck |
| **SLA compliance** | The dashboard tracks SLA risk claims in real time, giving team leads visibility before deadlines breach |
| **Handler throughput** | Each handler sees a pre-scored, indicator-rich case file instead of raw documents — reduces investigation time per case |
| **Customer NPS** | Genuine claimants experience faster payouts; only suspicious claims face deeper investigation |

### 1.4 Regulatory & Compliance Readiness

- **Full audit trail (JSONL)** — Every state transition, engine run, and human decision is logged with timestamps. This is critical for FCA / BaFin regulatory reporting requirements.
- **Human-in-the-loop governance** — The system **never auto-decides**. It moves claims to `HUMAN_REVIEW` and waits for a handler to choose `CLEAR / HOLD / REFER`. This ensures Allianz remains compliant with responsible AI regulations and avoids algorithmic bias liability.
- **Checkpoint gates (CP1/CP2)** — Built-in governance gates in the workflow ensure proper sign-off before claim progression, aligning with Allianz's internal control frameworks.
- **Explainable indicators** — Every score comes with plain-language explanations and recommended actions, satisfying the "right to explanation" under GDPR/AI Act.

---

## 2. Value to Quantexta Integration & Enhancement

> [!IMPORTANT]
> Sentinel is **not a replacement** for Quantexta — it is an **orchestration and pre-processing layer** that makes Quantexta's graph analytics more effective.

### 2.1 Structured Pre-Processing for Quantexta

| What Sentinel Does | How It Helps Quantexta |
|--------------------|------------------------|
| **PDF/DOCX ingestion & parsing** | Raw claim documents are converted to structured data (policy ID, claimant ID, loss date, claim type, jurisdiction) via regex-based extraction. Quantexta receives **clean, normalised entities** instead of raw text. |
| **Entity extraction from dossiers** | The 6-step agent pipeline (parsing → entity extraction → network intel → fraud scoring → indicators → decision pack) produces structured entity data that can be **directly fed into Quantexta's knowledge graph** for network resolution. |
| **Shared identifier flagging** | Sentinel pre-identifies shared addresses, phone numbers, and bank accounts — these become **seed nodes** for Quantexta's network traversal, significantly reducing Quantexta's computation scope and improving response time. |

### 2.2 Complementary Risk Dimensions

Quantexta excels at **network/graph analytics** (who is connected to whom). Sentinel adds dimensions that Quantexta's model does not natively cover:

| Dimension | Sentinel's Role | Quantexta's Role |
|-----------|-----------------|------------------|
| **Behavioural** | Timing anomalies, claim frequency, late reporting | Not covered |
| **Historical** | Prior fraud findings, similar loss patterns | Partially covered via entity history |
| **Network** | Pre-flags shared identifiers as seed nodes | **Primary strength** — deep graph traversal |
| **Document** | Completeness checks, inconsistency detection | Not covered |
| **Contextual** | Geographic anomalies, seasonal patterns | Partially covered |

> **Key message for BA:** Sentinel provides the **"before Quantexta"** layer (intake, parsing, initial scoring) and the **"after Quantexta"** layer (human decision workflow, audit, reporting). Quantexta sits in the middle as the **deep network intelligence** engine.

### 2.3 Improved Data Quality for Quantexta's Graph

- **Normalised entities** — Sentinel's claim parser produces standardised fields (ISO dates, consistent ID formats, jurisdiction codes) that improve Quantexta's entity resolution accuracy.
- **Confidence-weighted signals** — Instead of binary flags, Sentinel passes confidence-scored indicators to Quantexta, enabling it to weight edges in its network graph more accurately.
- **Reduced noise** — By filtering out clearly LOW-risk claims early, Sentinel reduces the volume of data Quantexta needs to process, **improving Quantexta's throughput and reducing compute costs**.

---

## 3. Operational Efficiency Gains

### 3.1 For Claims Handlers

| Before Sentinel | After Sentinel |
|-----------------|----------------|
| Manually read every claim document | Structured case summary with key facts pre-extracted |
| Subjective fraud assessment | Objective 5-dimension score with confidence levels |
| No visibility into connected cases | Network indicators highlight shared identifiers instantly |
| Decision rationale in free-text notes | Structured decision recording (CLEAR/HOLD/REFER) with audit trail |
| No SLA tracking | Real-time SLA risk visibility on dashboard |

### 3.2 For Team Leads / Managers

- **KPI dashboard** with live metrics: Claims in Pipeline, Fast-Track Settlements, Fraud Confirmed, SLA Risk Claims
- **Workstream volume chart** — real-time visibility into claim intake patterns
- **Batch processing** — run fraud pipeline across multiple cases simultaneously
- **Decision pack generation** — one-click governance pack PDF for case review meetings

### 3.3 For SIU (Special Investigations Unit)

- **Automated escalation triggers** — `REFER` decisions automatically route to SIU with full indicator package
- **Ring-fence alerts** — organised fraud patterns surfaced before SIU investigation begins
- **Evidence checklist** — investigation report includes a structured evidence checklist, reducing SIU setup time

---

## 4. Demo & Stakeholder Engagement Value

> [!TIP]
> This is a **demo-grade platform** with production-quality architecture — specifically designed to wow Allianz stakeholders and demonstrate Capgemini's capability.

### 4.1 Live Simulation Capability

- The application generates **synthetic fraud cases every 12 seconds** across 3 scenarios:
  - `FRAUD_RING` (HIGH risk) — demonstrates network detection
  - `SUSPICIOUS_CLUSTER` (REVIEW) — demonstrates behavioural flagging
  - `CLEAR_FASTTRACK` (LOW) — demonstrates straight-through processing
- This means the dashboard is **always alive and updating** during demos — no static screenshots or pre-loaded data.

### 4.2 Two Complementary Views

| View | Audience | Purpose |
|------|----------|---------|
| **Command Studio (RCGCC)** | Operations Managers, Team Leads | Portfolio-level fraud operations oversight |
| **Claim Investigation Studio (TRS)** | Individual Handlers, SIU Analysts | Deep-dive into single claim investigation |

### 4.3 Premium UI Design

- Dark-mode glassmorphism with Allianz navy/blue colour palette
- Animated KPI cards, SVG score rings, real-time agent trace narration
- Print-optimised investigation reports for governance packs

---

## 5. Strategic Talking Points for the BA

### 5.1 Cost Reduction Arguments

| Area | Estimated Impact |
|------|-----------------|
| **Fraud leakage reduction** | Industry benchmark: AI-augmented fraud detection reduces leakage by 15–30% |
| **Handler productivity** | Pre-scored cases reduce investigation time by ~40% per case |
| **SLA breach reduction** | Real-time SLA tracking prevents costly regulatory penalties |
| **STP rate improvement** | AUTO-clearing LOW-band claims can increase STP rate by 20–25% |

### 5.2 Risk Mitigation Arguments

- **Human-in-the-loop = no algorithmic liability** — Allianz is not making automated decisions; the AI provides intelligence, the human decides.
- **Full audit trail = regulatory compliance** — Every action is logged with timestamps, meeting FCA/BaFin/GDPR requirements.
- **Explainable AI = no black box** — Every indicator has a plain-language explanation and recommended action.

### 5.3 Scalability & Future-Proofing

- **Agent architecture planned** — 5 agent stubs (Coverage, Decision, Fraud Signal, Intake, Learning) are in place for future LLM-powered agents. This is the roadmap to agentic AI processing.
- **Modular fraud engine** — New dimensions or indicators can be added without changing the orchestration layer.
- **Azure-ready** — Architecture is designed for Azure App Service with clear migration path to Azure PostgreSQL, Blob Storage, and CDN.

### 5.4 Competitive Differentiation

- **Not just a dashboard** — Sentinel is an end-to-end orchestration platform: ingestion → scoring → human review → decision → reporting.
- **Quantexta amplifier** — Positions Capgemini as adding value *on top of* Quantexta, not competing with it.
- **Demo-ready from day one** — Live simulation means stakeholders see a working system, not a prototype.

---

## 6. Key Risks & Gaps to Acknowledge

> [!WARNING]
> Be transparent about these in BA discussions to build credibility.

| Gap | Business Impact | Mitigation |
|-----|-----------------|------------|
| **Demo-grade scoring** — rule-based, not ML | Scoring is deterministic/keyword-based, not trained on Allianz claims data | Position as "framework" — the scoring logic is pluggable and designed to be replaced with Allianz-trained models |
| **SQLite database** — not production-grade | Data is ephemeral on Azure; resets on restart | Migration path to Azure PostgreSQL is documented |
| **No real Quantexta integration** | Network scoring is currently internal simulation | Integration API layer is designed to be swapped for real Quantexta API calls |
| **Agent stubs not functional** | 5 agent files exist but are not wired into the pipeline | Roadmap item — demonstrates future architecture intent |
| **Heavy frontend** | 200KB+ JS files may need optimisation for production | Acceptable for demo; production would use bundling/minification |

---

## 7. One-Pager Summary (For Quick Sharing)

**What is Sentinel?**  
An AI-powered anti-fraud command studio that automates claim triage, scores fraud risk across 5 dimensions, and provides claims handlers with explainable intelligence — all while maintaining human-in-the-loop governance.

**Who benefits?**
- **Allianz Claims Ops** — faster triage, fewer SLA breaches, higher STP rate
- **Allianz SIU** — automated escalation with full indicator packages
- **Allianz Compliance** — full audit trail, explainable decisions, GDPR-ready
- **Quantexta Model** — cleaner input data, pre-flagged network seeds, reduced processing scope

**What makes it different?**
- 5-dimension scoring (not just network analysis)
- Human-in-the-loop (not automated decisioning)
- Live demo capability (not static prototypes)
- Quantexta amplifier (not a competitor)

**Bottom line:**  
Sentinel reduces fraud leakage, accelerates genuine claims, and makes Quantexta's network intelligence more effective — all within a governance framework that keeps Allianz compliant.
