import os
import json
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(
    api_key=os.environ.get("QWEN_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)

SYSTEM_PROMPT = """You are a WASH (Water, Sanitation, and Hygiene) public health risk assessment agent.

Given an incident report, assess the risk level and recommend an action.

Respond ONLY with valid JSON in this exact format:
{
  "risk_level": "high" | "medium" | "low",
  "risk_score": <number 1-10>,
  "key_concerns": ["concern1", "concern2"],
  "recommended_action": "immediate_escalation" | "routine_investigation" | "log_and_monitor",
  "requires_human_review": true | false,
  "summary": "brief explanation"
}

Risk level rules:
- HIGH: contaminated water source, outbreak risk, open defecation near water source, affects >50 people
- MEDIUM: partial sanitation failure, hygiene facility breakdown, affects 10-50 people
- LOW: minor hygiene issue, isolated incident, affects <10 people"""

@app.route("/assess", methods=["POST"])
def assess_risk():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON body provided"}), 400

        required_fields = ["location", "incident_description"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        report_text = f"""
Location: {data.get('location', 'Unknown')}
Report Channel: {data.get('report_channel', 'Unknown')}
Incident Description: {data['incident_description']}
Reporter Name: {data.get('reporter_name', 'Anonymous')}
Date Reported: {data.get('reported_date', 'Unknown')}
"""

        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Assess this WASH incident report:\n{report_text}"}
            ],
            temperature=0.1
        )

        raw = response.choices[0].message.content.strip()
        assessment = json.loads(raw)

        result = {
            "case_id": data.get("case_id", "WASH-UNKNOWN"),
            "assessment": assessment,
            "routing": {
                "escalate_immediately": assessment["risk_level"] == "high",
                "assign_to": "senior_health_officer" if assessment["risk_level"] == "high" else "field_officer",
                "sla_hours": 4 if assessment["risk_level"] == "high" else 48 if assessment["risk_level"] == "medium" else 120
            }
        }

        return jsonify(result), 200

    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse model response as JSON", "raw": raw}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "WASH Risk Assessment Agent"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)