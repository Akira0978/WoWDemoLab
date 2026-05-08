# Sentinel Fraud Intelligence Platform — Executive Summary

## Overview
Sentinel is a full-stack, agentic fraud intelligence demonstration platform that simulates real-world insurance fraud detection workflows. It combines UI reuse, backend orchestration, document ingestion, and synthetic data generation to deliver a realistic, interactive experience.

---

## Objectives
- Build a **realistic fraud detection system demo**
- Reuse existing enterprise UI (RCGCC + TenderResponseStudio)
- Simulate **live claim intake and processing**
- Provide **end-to-end workflow (ingest → analyze → decide)**

---

## Architecture

### 1. UI Layer
- **RCGCC (Home)**: Real-time case hub displaying incoming claim cases
- **TenderResponseStudio (Detail)**: Deep-dive claim analysis and decision interface

### 2. Backend Layer
- Flask-based API services
- Modular endpoints for claims, ingestion, analysis, audit, simulation

### 3. Data Layer
- `ClaimCase` entity storing:
  - Identity (case_id, policy_id, claimant_id)
  - Source document (filename, text)
  - Parsed ingestion
  - Fraud intelligence (score, band, confidence)
  - Lifecycle status
  - Audit trail

---

## Core Processing Pipeline

Input (PDF/DOCX or synthetic text)
    ↓
Text Extraction (document_utils)
    ↓
Claim Parsing (claim_parser)
    ↓
Signal Detection (heuristics)
    ↓
Fraud Analysis (runner / scoring_engine)
    ↓
Results stored in ClaimCase
    ↓
Audit logging

---

## Simulation Engine

### fraud_datagen.py
- Generates 20–30 realistic cases
- Includes different scenarios:
  - Fraud rings (high risk)
  - Suspicious clusters (medium risk)
  - Clean fast-track claims (low risk)

### Live Feed
- API: `/api/sim/start`
- Inserts one case every 10–15 seconds
- RCGCC auto-refresh shows dynamic stream

---

## User Flows

### 1. RCGCC → Studio
- User clicks case row
- Studio opens
- Auto-ingestion triggers using pre-generated document
- Analysis runs automatically
- Fraud output displayed

### 2. Direct Studio Upload
- User uploads PDF/DOCX
- System extracts + parses document
- Case is created or updated
- Analysis executes

### 3. Continuous Feed
- Simulation engine adds cases in background
- RCGCC acts as live case hub

---

## Outputs
- Fraud Score (0–100)
- Fraud Band (LOW / REVIEW / HIGH)
- Confidence Score
- Indicators (explainable features)
- Audit Logs (traceable events)
- Decision states (CP0–CP2)

---

## Key Capabilities
- Document ingestion (PDF/DOCX)
- Real-time case streaming
- Explainable fraud scoring
- Agent-based workflow orchestration
- Audit traceability
- Human decision checkpoints

---

## System Differentiators
- UI reused without structural changes
- Backend-driven intelligence layer
- Simulated yet realistic fraud patterns
- Continuous data generation
- Full lifecycle coverage (ingest → detect → decide)

---

## Demo Narrative

1. Claims arrive continuously into system
2. Each claim has an attached document
3. System ingests and parses document
4. AI agents evaluate fraud likelihood
5. Outputs include score and explanation
6. Human checkpoints finalize decision

---

## Final State

Sentinel is a fully functioning:

**Real-time, document-driven fraud intelligence platform demo**

It showcases not just UI, but a realistic backend-powered system capable of:
- Dynamic data ingestion
- Automated fraud analysis
- Explainable outputs
- Decision governance

---

## Future Enhancements
- Network graph visualization (fraud rings)
- LLM-based advanced parsing
- Real-time alerting system
- Integration with external data sources
