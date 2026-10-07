# Incident Response Agent: 3-Minute Presenter Walkthrough & Demo Guide

**Project:** Incident Response Agent  
**Tagline:** *"An AI agent that remembers how your organization solved problems before."*  
**Architecture:** FastAPI + Official Hindsight Client/Server (`incident-response-bank`) + React/TypeScript SRE Console  

---

## Executive Summary & Core Value Proposition

Modern engineering teams suffer from repeated production outages because post-mortem lessons are scattered across Jira tickets, Google Docs, and Slack channels. Standard LLMs hallucinate or lack institutional memory.

This prototype demonstrates a **closed-loop organizational learning engine**:
1. When an incident occurs, the agent queries the **real Hindsight memory engine** (`arecall()`).
2. It fuses real-time telemetry with historical post-mortems and runbooks, strictly distinguishing **Current Evidence** from **Historical Precedents**.
3. **The Human SRE remains in control:** Remediation requires human approval.
4. Upon human sign-off, the verified post-mortem is retained back into Hindsight (`aretain()`), elevating the organization's collective intelligence for future fire drills.

---

## 3-Minute Live Presenter Script

### [0:00–0:30] — The Problem: Amnesiac Incident Response

| Section | Details |
| :--- | :--- |
| **What Presenter Says** | *"Every engineering leader knows the pain of resolving an incident, writing a thorough post-mortem, and then—three months later—watching another team spend four hours troubleshooting the exact same issue from scratch. Standard AI assistants can read logs, but they have complete amnesia across incidents. We built the Incident Response Agent to solve this: an AI system with persistent organizational memory that actually remembers how your team resolved problems before."* |
| **What Presenter Clicks** | Navigate to the **Dashboard** (`http://127.0.0.1:8000/` or port `5173`). Highlight the **Hindsight Status Pill** in the top navigation. |
| **What Appears on Screen** | SRE Command Center dashboard showing active incidents, P1 counters, and the green pulsing badge: `Hindsight: CONNECTED (Bank: incident-response-bank)`. |
| **Key Point for Judges** | This is connected to a **live, official Hindsight server**, not a simulated mock or toy vector DB. |

---

### [0:30–1:10] — Step 1: Cold Start (INC-001 — Payment API Connection Pool Exhaustion)

| Section | Details |
| :--- | :--- |
| **What Presenter Says** | *"Let's start with a cold-start scenario. Here is INC-001: our Payment API is suffering latency spikes due to database connection starvation during a promotional campaign. Because this is our first time seeing this failure mode, there are zero historical precedents in our memory bank."*<br/><br/>*(Clicks 'Run Hindsight Analysis')*<br/><br/>*"The agent analyzes current telemetry, checks the Payment API runbook, and formulates a hypothesis. As the SRE on call, I review the diagnostic trace and approve the fix: increasing the connection pool size and adjusting timeouts. Notice what happens when I click 'Approve & Retain Memory': the verified solution is committed directly into our Hindsight memory bank. The system has now learned."* |
| **What Presenter Clicks** | 1. Click **INC-001** on the Guided Demo Bar (or Incidents list).<br/>2. Click **Run Hindsight Analysis**.<br/>3. Review the 6-Step Diagnostic Trace (Step 1: Evidence, Step 2: Recall, Step 5: Hypotheses).<br/>4. Click **SRE Sign-Off** $\to$ Click **Confirm & Retain**. |
| **What Appears on Screen** | - **Diagnostic Trace:** Shows 0 historical precedents found; hypothesis marked `[CURRENT EVIDENCE]`.<br/>- **Confirmation Modal:** Displays green success banner: *"Retained to Hindsight bank 'incident-response-bank' with Memory ID: INC-001-hindsight"* with the structured post-mortem snippet. |
| **Key Point for Judges** | **The human remains the decision-maker.** AI hypotheses are never retained automatically; only human-verified post-mortems enter organizational memory. |

---

### [1:10–1:55] — Step 2: The Same Pattern Recurs (INC-002 — Payment API Recurrence)

| Section | Details |
| :--- | :--- |
| **What Presenter Says** | *"Three weeks later, another incident strikes the Payment API: INC-002. Different logs, different traffic volume, but similar symptoms. Let's run analysis."*<br/><br/>*(Clicks 'Run Hindsight Analysis')*<br/><br/>*"Look at the diagnostic trace now: Step 2 shows the agent queried Hindsight. In Step 3, it retrieved our previous INC-001 post-mortem with genuine semantic and reranker scores from the Hindsight engine! In Step 5, the lead hypothesis is explicitly tagged as 'HISTORICAL PRECEDENT — INC-001' with 94% confidence, citing our exact prior resolution. The agent didn't have to guess or trial-and-error; it immediately recognized the pattern."* |
| **What Presenter Clicks** | 1. Click **INC-002** on the Guided Demo Bar.<br/>2. Click **Run Hindsight Analysis**.<br/>3. Open Step 3 (Historical Precedents) and Step 5 (Root-Cause Hypotheses) in the Diagnostic Trace. |
| **What Appears on Screen** | - **Evidence Provenance Badge:** Purple `[HISTORICAL PRECEDENT - INC-001]` badge.<br/>- **Genuine Scores:** Displays Hindsight reranker, semantic, and final scores.<br/>- **Rationale:** Explicitly quotes the INC-001 confirmed fix: *"Increase database connection pool size from 10 to 50 in Helm values and set connection-timeout to 3000ms"*. |
| **Key Point for Judges** | **Observable reasoning change:** The model did not just retrieve a document; its hypothesis and confidence directly shifted based on institutional memory. |

---

### [1:55–2:25] — The Head-to-Head: With Memory vs Without Memory

| Section | Details |
| :--- | :--- |
| **What Presenter Says** | *"To prove how much difference this memory makes, let's open our live comparative view. On the left is an isolated LLM with zero memory context. On the right is our Hindsight-augmented agent. Both sides are powered by live backend responses."*<br/><br/>*"Notice the contrast: Without memory, the isolated model produces generic trial-and-error hypotheses (70% confidence) and misses the previous fix entirely. With Hindsight, the agent immediately cites the INC-001 precedent, raises confidence to 94%, and delivers targeted remediation without unnecessary service disruption."* |
| **What Presenter Clicks** | Click **Compare With/Without Memory** in the top action bar of INC-002. |
| **What Appears on Screen** | Side-by-side comparative console:<br/>- **Left (Without Memory):** 0 precedents recalled, generic database bottleneck hypothesis (`[CURRENT EVIDENCE]`), generic investigation steps.<br/>- **Right (With Hindsight Memory):** INC-001 precedent recalled with genuine Hindsight scores, precedent-informed hypothesis (`[HISTORICAL PRECEDENT]`), targeted remediation plan.<br/>- **Metrics Bar:** 0 vs 1+ precedents, 70% vs 94% confidence. |
| **Key Point for Judges** | **Zero fabrication:** Everything on screen is rendered dynamically from `/api/agent/analyze-isolated/INC-002` and `/api/agent/analyze/INC-002`. Close modal, confirm INC-002. |

---

### [2:25–2:50] — Step 3: Cross-Service Learning Transfer (INC-003 — Order Service)

| Section | Details |
| :--- | :--- |
| **What Presenter Says** | *"Now for the most powerful capability: cross-service knowledge transfer. INC-003 is NOT in Payment API—it is in the Order Service, an entirely different microservice experiencing connection pool deadlocks under heavy order volume."*<br/><br/>*(Clicks 'Run Hindsight Analysis')*<br/><br/>*"When the agent queries Hindsight, it retrieves the connection pool lessons learned originally in the Payment API! It recognizes that database pool sizing is an organizational best practice across services, not just an isolated microservice quirk. The Order Service SRE confirms the recommendation, retaining this cross-service standard into Hindsight."* |
| **What Presenter Clicks** | 1. Click **INC-003** on the Guided Demo Bar.<br/>2. Click **Run Hindsight Analysis**.<br/>3. Inspect Step 3 and top hypothesis showing cross-service pool transfer.<br/>4. Click **SRE Sign-Off** $\to$ Click **Confirm & Retain**. |
| **What Appears on Screen** | - Target Service: `Order Service`.<br/>- Recalled Precedents: Shows memory retrieved from Payment API pool resolution.<br/>- Confirmation: INC-003 post-mortem committed to memory. |
| **Key Point for Judges** | **Organizational Scaling:** Institutional knowledge does not stay siloed inside one service; it elevates the operational baseline of the entire engineering organization. |

---

### [2:50–3:10] — The Organizational Learning Architecture & Takeaway

| Section | Details |
| :--- | :--- |
| **What Presenter Says** | *"Let's look at the complete organizational loop. Here on our Memory Audit tab, you see the immutable audit trail of every recall, confirmation, and retention. When we open our Learning Architecture view, you see the complete cycle: Incidents generate evidence $\to$ Hindsight recalls past experience $\to$ Agent proposes root causes $\to$ Human confirms $\to$ Hindsight retains new memory $\to$ Future incidents resolve faster with higher confidence. This is how modern engineering organizations stop repeating yesterday's mistakes."* |
| **What Presenter Clicks** | 1. Click **Memory Audit** in navigation tab to show the chronological event log.<br/>2. Click **Learning Loop Architecture** (in the Guided Demo bar). |
| **What Appears on Screen** | - **Memory Audit Log:** Complete list of RETAIN and RECALL operations with latency and bank ID.<br/>- **Learning Loop Modal:** Interactive 10-step conceptual diagram highlighting human-in-the-loop governance and Hindsight memory banking. |
| **Key Point for Judges** | Clear, cohesive narrative: SRE workflows become progressively smarter over time through persistent, provenanced AI memory. |

---

## 60-Second Backup Demo Path (For Time-Constrained Pitches)

When presented with a hard 1-minute time limit:

1. **[0:00–0:15] The Hook & Problem:**
   - *"Software teams repeatedly resolve the same outages because incident post-mortems are scattered and LLMs have amnesia. This prototype gives AI persistent organizational memory via Google DeepMind Hindsight."*
   - Show Dashboard with live `Hindsight: CONNECTED` indicator.

2. **[0:15–0:40] The Concrete Value (INC-002 with Comparison):**
   - Click **INC-002** $\to$ Click **Compare With/Without Memory**.
   - Point to both columns:
     - *"On the left: Without memory, an isolated LLM guesses blindly with 70% confidence."*
     - *"On the right: With Hindsight, it recalls our confirmed INC-001 post-mortem with genuine reranker scores, identifies the root cause with 94% confidence, and applies the proven fix."*

3. **[0:40–1:00] Human Sign-off & Continuous Learning:**
   - Close modal $\to$ Click **SRE Sign-Off** $\to$ Click **Confirm & Retain**.
   - Click **Memory Audit** to show the live retention event.
   - Closing sentence: *"The human remains the decision maker, while Hindsight ensures the organization never forgets a lesson learned."*

---

## Live Demo Safety Checklist & Fallback Strategy

| Check | Expected Value | Status |
| :--- | :--- | :--- |
| **Hindsight Server Reachable** | `http://127.0.0.1:8888/health` returns `200 healthy` | Verified |
| **Memory Bank** | `incident-response-bank` | Verified |
| **INC-001, INC-002, INC-003 Baseline** | Reset to `Investigating` / unconfirmed via **Reset Demo** | Verified |
| **Isolated Analysis Endpoint** | `POST /api/agent/analyze-isolated/{id}` returns HTTP 200 | Verified |
| **Hindsight Analysis Endpoint** | `POST /api/agent/analyze/{id}` returns HTTP 200 with genuine scores | Verified |
| **Confirmation Endpoint** | `POST /api/agent/confirm/{id}` returns HTTP 200 and triggers `aretain()` | Verified |
| **Memory Timeline Audit Log** | `GET /api/memory/timeline` returns chronological events | Verified |
| **Fallback / Error Handling** | If Hindsight server goes offline, UI immediately shows red disconnected pill and alerts that retention is pending rather than claiming false success | Verified |

---

## Resetting the Demo for Another Run

To reset the demonstration at any time:
1. Click the **Reset Demo** button in the top navigation bar, or
2. Run `python -m pytest tests/test_incidents_api.py -k test_reset_demo_state -q` in the backend.
This cleans demo analyses and resets `INC-001`, `INC-002`, and `INC-003` to un-retained status so the story can be presented again from scratch.
