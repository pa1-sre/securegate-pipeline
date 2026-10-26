import os
import json
import urllib.request
import urllib.error

def load_json_safely(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Failed to parse {filepath}: {str(e)}"}
    return {"status": "No findings file reported or clean"}

def aggregate_reports():
    return {
        "gitleaks": load_json_safely("gitleaks-results.json"),
        "trivy": load_json_safely("trivy-results.json"),
        "zap_dast": load_json_safely("report_json.json")
    }

def call_gemini_flash(scan_data):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ `GEMINI_API_KEY` secret is missing. AI Triage skipped cloud analysis."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
You are a DevSecOps AI Assistant analyzing pipeline scan results for "SecureGate".
Summarize the findings into a clean, professional, plain-English executive report card for the developer.

Structure your output precisely as follows:
1. 🚦 **Overall Security Posture** (Pass / Needs Attention / Critical Failure)
2. 🔑 **Secret Detection (Gitleaks)**
3. 📦 **Dependency Vulnerabilities (Trivy)**
4. 🌐 **Dynamic Application Testing (OWASP ZAP)**
5. 💡 **Top 3 Priority Remediation Actions**

Raw Scan Payload:
{json.dumps(scan_data, indent=2)[:6000]}
"""

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            return res["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Error connecting to Gemini API: {str(e)}"

if __name__ == "__main__":
    data = aggregate_reports()
    report = call_gemini_flash(data)
    
    with open("ai_summary.md", "w") as f:
        f.write(report)
    print("AI Triage summary generated successfully.")
