# WASH Risk Assessment Agent

An AI-powered public health agent that assesses Water, Sanitation, and Hygiene (WASH) incident reports and automatically routes them based on risk severity. Built for the Global AI Hackathon Series with Qwen Cloud (Track 4: Autopilot Agent).

## Problem

In under-resourced public health systems across sub-Saharan Africa, WASH incident reports are handled manually — paper-based, siloed, and slow. A contaminated borehole serving 200 residents might sit in a queue for days before a health officer even sees it. Delays cost lives.

## Solution

This agent accepts a WASH incident report (submitted via text, voice transcript, photo description, or structured form), reasons over it using Qwen's frontier AI model, and instantly returns:

- A **risk level** (high / medium / low)
- A **risk score** (1–10)
- **Key concerns** identified in the report
- A **routing decision** (immediate escalation vs. routine investigation vs. log and monitor)
- An **SLA** (4 hours for high-risk, 48 hours for medium, 120 hours for low)
- A **human review flag** for critical cases

## Architecture
Reporter → POST /assess → Alibaba Cloud Function Compute (Singapore)
↓
Flask API (Python 3.12)
↓
Qwen Cloud API (qwen-plus model)
↓
Risk Assessment + Routing Decision
↓
JSON Response

## Tech Stack

- **AI Model:** Qwen Cloud (qwen-plus) via DashScope International API
- **Backend:** Python 3.12 + Flask
- **Deployment:** Alibaba Cloud Function Compute 3.0 (Singapore, ap-southeast-1)
- **Runtime:** Custom Runtime / Debian 12

## Live Endpoint
https://wash-risk-agent-hwfcbnykfb.ap-southeast-1.fcapp.run

## API Usage

### Assess a WASH Incident

```bash
curl -X POST https://wash-risk-agent-hwfcbnykfb.ap-southeast-1.fcapp.run/assess \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "WASH-001",
    "location": "Karu LGA, Abuja FCT, Nigeria",
    "report_channel": "text",
    "incident_description": "Community borehole contaminated with sewage overflow. 200 residents affected. Children showing diarrhea symptoms.",
    "reporter_name": "Community Health Worker",
    "reported_date": "2026-07-01"
  }'
```

### Sample Response

```json
{
  "case_id": "WASH-001",
  "assessment": {
    "risk_level": "high",
    "risk_score": 9,
    "key_concerns": ["contaminated water source", "outbreak risk", "affects >50 people"],
    "recommended_action": "immediate_escalation",
    "requires_human_review": true,
    "summary": "Sewage contamination of a community borehole serving 200 residents with confirmed diarrhea cases indicates high risk of waterborne disease outbreak."
  },
  "routing": {
    "escalate_immediately": true,
    "assign_to": "senior_health_officer",
    "sla_hours": 4
  }
}
```

### Health Check

```bash
curl https://wash-risk-agent-hwfcbnykfb.ap-southeast-1.fcapp.run/health
```

## Setup

1. Clone this repo
2. Create a Qwen Cloud account and get an API key from https://home.qwencloud.com/api-keys
3. Deploy to Alibaba Cloud Function Compute with `QWEN_API_KEY` as an environment variable
4. Install dependencies: `pip3 install openai flask -t .`

## Real-World Impact

This agent is built on domain expertise from Nigeria's public health system — the risk scoring logic reflects real WASH indicators (water source type, population affected, symptom reports, sanitation proximity) used by environmental health officers on the ground. The builder holds a NEBOSH IGC certification and is a Licensed Environmental Health Officer (EHORECON).

## License

MIT
