"""
Quick manual test of the entire pipeline without Docker
Useful for development and testing before containerization
"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from qr_decoder import QRDecoder
from heuristics import HeuristicAnalyzer
from ai_analyzer import AIAnalyzer


def test_pipeline():
    """Test complete analysis pipeline locally"""
    
    print("\n" + "=" * 70)
    print("QuishGuard - Local Pipeline Test")
    print("=" * 70)
    
    # Initialize components
    print("\n📦 Initializing components...")
    decoder = QRDecoder()
    heuristics = HeuristicAnalyzer()
    ai = AIAnalyzer()
    print("   ✓ QR Decoder ready")
    print("   ✓ Heuristics Analyzer ready")
    print("   ✓ AI Analyzer ready")
    
    # Test cases
    test_cases = [
        {
            "name": "Legitimate PayPal URL",
            "content": "https://paypal.com",
            "expected_risk": "LOW"
        },
        {
            "name": "Suspicious Lookalike URL",
            "content": "https://paytm-verify.xyz/secure/login",
            "expected_risk": "HIGH"
        },
        {
            "name": "Legitimate UPI Link",
            "content": "upi://pay?pa=merchant@okhdfcbank&pn=PayTM&am=100",
            "expected_risk": "LOW"
        },
        {
            "name": "Suspicious UPI Link",
            "content": "upi://pay?pa=randomuser123@gmail.com&pn=Verify&am=500",
            "expected_risk": "MEDIUM"
        },
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─' * 70}")
        print(f"Test {i}: {test['name']}")
        print(f"{'─' * 70}")
        
        content = test['content']
        print(f"\n  Input: {content}")
        
        # Step 1: Heuristics
        print("\n  Step 1: Analyzing with heuristics...")
        heuristics_result = heuristics.analyze(content)
        print(f"    Type detected: {heuristics_result['type']}")
        print(f"    Signals found:")
        for signal in heuristics_result['extracted_signals']:
            print(f"      • {signal}")
        
        # Step 2: AI Analysis
        print("\n  Step 2: AI analysis...")
        try:
            verdict = ai.analyze(content, heuristics_result)
            
            print(f"\n  🎯 VERDICT:")
            print(f"    Risk Level: {verdict['risk_level']} (expected: {test['expected_risk']})")
            print(f"    Scam Type: {verdict['scam_type']}")
            print(f"    Explanation: {verdict['explanation']}")
            
            if verdict['red_flags']:
                print(f"    Red Flags:")
                for flag in verdict['red_flags']:
                    print(f"      ⚠️  {flag}")
            
            print(f"    Recommendation: {verdict['recommendation']}")
            
        except Exception as e:
            print(f"\n  ⚠️  AI Analysis failed: {e}")
            print(f"     Make sure GOOGLE_API_KEY is set: export GOOGLE_API_KEY='your-key'")
    
    print(f"\n{'=' * 70}")
    print("Test Complete!")
    print("=" * 70)
    print("\nTo run with Docker:")
    print("  1. Get free key: https://aistudio.google.com/app/apikeys")
    print("  2. Set GOOGLE_API_KEY in .env")
    print("  3. Run: docker-compose up")
    print("  4. Open: http://localhost:3000")
    print()


if __name__ == "__main__":
    # Check for API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("\n⚠️  GOOGLE_API_KEY environment variable not set")
        print("   Get free key: https://aistudio.google.com/app/apikeys")
        print("   Set it: export GOOGLE_API_KEY='your-key-here'")
        print("\n   Continuing with local tests that don't need API key...\n")
    
    test_pipeline()
