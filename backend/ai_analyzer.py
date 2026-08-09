"""
Phase 3: AI Reasoning Layer
Use Google Gemini to analyze decoded content + heuristics and provide fraud verdict
"""
import json
import os
import re
from typing import Dict, Any, Optional
from google import genai


class AIAnalyzer:
    """Use Google Gemini to perform fraud analysis reasoning"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Google GenAI client"""
        key = api_key or os.getenv('GOOGLE_API_KEY')
        if key:
            self.client = genai.Client(api_key=key)
        else:
            self.client = None

    def analyze(self, decoded_content: str, heuristics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send decoded content + heuristics to Gemini for fraud analysis.

        Args:
            decoded_content: Raw decoded string from QR
            heuristics: Output from HeuristicAnalyzer.analyze()

        Returns:
            Structured verdict with scam_type, risk_level, explanation, red_flags
        """
        if not self.client:
            return self._error_verdict("GOOGLE_API_KEY not configured")

        # Build context for Gemini
        signals_text = "\n".join([f"- {signal}" for signal in heuristics.get('extracted_signals', [])])

        prompt = f"""You are a fraud detection expert analyzing QR codes in India, specifically focused on UPI payment fraud and phishing scams.

A QR code was scanned with the following details:

**Decoded Content:**
{decoded_content}

**Content Type:** {heuristics.get('type', 'unknown')}

**Extracted Signals from Heuristic Analysis:**
{signals_text}

**Parsed Data:**
{json.dumps(heuristics.get('structured_data', {}), indent=2)}

Based on this information, provide a security assessment. Be concise but thorough. Respond in valid JSON format with these fields:
- scam_type: One of [upi_fraud, phishing, malware, suspicious_app, legitimate, unknown]
- risk_level: One of [LOW, MEDIUM, HIGH, CRITICAL]
- explanation: Brief 1-2 sentence explanation for a non-technical person
- red_flags: List of specific warning signs (max 3-4 items)
- recommendation: What should the user do?

Example response format:
{{
    "scam_type": "legitimate",
    "risk_level": "LOW",
    "explanation": "This appears to be a legitimate payment QR from a recognized vendor.",
    "red_flags": [],
    "recommendation": "Safe to scan and complete payment."
}}

Analyze and respond with valid JSON only."""

        # Try models in order of preference (handles per-model rate limits)
        models = ['gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-1.5-flash']

        for model_name in models:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                response_text = response.text

                # Parse JSON from response
                try:
                    verdict = json.loads(response_text)
                    return self._validate_verdict(verdict)
                except json.JSONDecodeError:
                    # Try to extract JSON if wrapped in markdown code fences or other text
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        verdict = json.loads(json_match.group())
                        return self._validate_verdict(verdict)
                    else:
                        return self._error_verdict("Could not parse AI response as JSON")

            except Exception as e:
                error_str = str(e)
                print(f"Error calling Gemini ({model_name}): {e}")
                # If rate limited, try next model
                if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
                    continue
                # For other errors, don't retry
                return self._error_verdict(f"API Error: {error_str}")

        return self._error_verdict("All Gemini models rate-limited. Please retry in a minute.")

    def _validate_verdict(self, verdict: Dict[str, Any]) -> Dict[str, Any]:
        """Validate verdict has required fields with valid values"""
        required_fields = ['scam_type', 'risk_level', 'explanation', 'red_flags', 'recommendation']
        # Ensure all fields exist
        for field in required_fields:
            if field not in verdict:
                verdict[field] = None

        # Validate enum values
        valid_scam_types = ['upi_fraud', 'phishing', 'malware', 'suspicious_app', 'legitimate', 'unknown']
        if verdict['scam_type'] not in valid_scam_types:
            verdict['scam_type'] = 'unknown'

        valid_risk_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        if verdict['risk_level'] not in valid_risk_levels:
            verdict['risk_level'] = 'MEDIUM'

        # Ensure red_flags is a list
        if not isinstance(verdict['red_flags'], list):
            verdict['red_flags'] = []

        return verdict

    def _error_verdict(self, error_msg: str) -> Dict[str, Any]:
        """Return a safe error verdict"""
        return {
            'scam_type': 'unknown',
            'risk_level': 'MEDIUM',
            'explanation': f"Could not complete analysis: {error_msg}. Exercise caution.",
            'red_flags': ['Analysis incomplete'],
            'recommendation': 'Do not scan unless you completely trust the source.'
        }


if __name__ == "__main__":
    from heuristics import HeuristicAnalyzer

    analyzer = AIAnalyzer()
    heuristics = HeuristicAnalyzer()

    # Test with suspicious UPI
    test_content = "upi://pay?pa=randomuser123@okhdfcbank&pn=Merchant&am=500"
    heuristics_result = heuristics.analyze(test_content)
    print("Analyzing with Gemini...")
    verdict = analyzer.analyze(test_content, heuristics_result)
    print(json.dumps(verdict, indent=2))
