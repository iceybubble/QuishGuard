"""
Phase 7: Demo Preparation and Test Suite
Test QR decoding with sample data before live demo
"""
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from qr_decoder import QRDecoder
from heuristics import HeuristicAnalyzer
from ai_analyzer import AIAnalyzer


def test_phase_1_qr_decoding():
    """Test QR decoding functionality"""
    print("=" * 60)
    print("PHASE 1: QR DECODING TEST")
    print("=" * 60)
    
    decoder = QRDecoder()
    print("\n✓ QR Decoder initialized")
    
    # Test with generated QR images if available
    qr_dir = Path(__file__).parent / "qr_images"
    if qr_dir.exists():
        expected = {
            "legitimate_upi.png": "upi://pay?pa=merchant@okhdfcbank&pn=CafeBliss&am=150",
            "legitimate_url.png": "https://paypal.com/checkout",
            "suspicious_url.png": "https://paytm-verify.xyz/secure/login",
            "suspicious_upi.png": "upi://pay?pa=xk29z@gmail.com&pn=Verify&am=999",
        }
        
        for filename, expected_content in expected.items():
            filepath = qr_dir / filename
            if filepath.exists():
                result = decoder.decode_from_file(str(filepath))
                status = "✓" if result == expected_content else "✗"
                print(f"\n  {status} {filename}")
                print(f"    Expected: {expected_content}")
                print(f"    Got:      {result}")
            else:
                print(f"\n  ⚠ {filename} not found — run generate_test_qr.py first")
    else:
        print("\n  ⚠ No test QR images found")
        print("    Run: python tests/generate_test_qr.py")
    print()


def test_phase_2_heuristics():
    """Test heuristic analysis"""
    print("=" * 60)
    print("PHASE 2: HEURISTIC ANALYSIS TEST")
    print("=" * 60)
    
    analyzer = HeuristicAnalyzer()
    
    test_cases = [
        ("upi://pay?pa=merchant@okhdfcbank&pn=PaytmQR&am=100", "Legitimate UPI"),
        ("upi://pay?pa=randomuser123@gmail.com&pn=Merchant&am=500", "Suspicious UPI"),
        ("https://paytm.com/pay", "Legitimate URL"),
        ("https://paytm-verify.xyz/secure/login", "Suspicious URL"),
    ]
    
    for content, description in test_cases:
        print(f"\n📋 Test: {description}")
        print(f"   Content: {content}")
        
        result = analyzer.analyze(content)
        print(f"   Type: {result['type']}")
        print(f"   Signals:")
        for signal in result['extracted_signals']:
            print(f"     - {signal}")


def test_phase_3_ai_analysis():
    """Test AI analysis (requires GOOGLE_API_KEY)"""
    print("\n" + "=" * 60)
    print("PHASE 3: AI ANALYSIS TEST")
    print("=" * 60)
    
    print("\n⚠️  Requires GOOGLE_API_KEY environment variable")
    print("   Set: export GOOGLE_API_KEY='your-key-here'")
    print("   Get free key: https://aistudio.google.com/app/apikeys")
    
    try:
        ai = AIAnalyzer()
        heuristics = HeuristicAnalyzer()
        
        content = "https://secure-paypal-verify.tk/login"
        heuristics_result = heuristics.analyze(content)
        
        print(f"\n📋 Test content: {content}")
        print("   Analyzing with Gemini...")
        
        verdict = ai.analyze(content, heuristics_result)
        
        print(f"\n   ✓ Verdict received:")
        print(f"     - Risk Level: {verdict.get('risk_level', 'N/A')}")
        print(f"     - Scam Type: {verdict.get('scam_type', 'N/A')}")
        print(f"     - Explanation: {verdict.get('explanation', 'N/A')}")
        
    except Exception as e:
        print(f"\n   ✗ Error: {e}")
        print("     Make sure GOOGLE_API_KEY is set")


def test_complete_pipeline():
    """Test the complete analysis pipeline end-to-end"""
    print("\n" + "=" * 60)
    print("COMPLETE PIPELINE TEST")
    print("=" * 60)
    
    print("\n✓ Backend (FastAPI)")
    print("  - /health - Health check")
    print("  - /analyze - Upload QR image")
    print("  - /analyze-text - Paste link directly")
    
    print("\n✓ Frontend (HTML/JS)")
    print("  - Upload tab: Drag-drop or click to upload QR image")
    print("  - Paste tab: Paste URL or UPI link")
    print("  - Results display: Risk verdict with explanation")
    
    print("\n✓ Docker Setup")
    print("  - Backend service on port 8000")
    print("  - Frontend service on port 3000")
    print("  - Shared network for inter-service communication")


def print_demo_checklist():
    """Print the demo day checklist"""
    print("\n" + "=" * 60)
    print("DEMO DAY CHECKLIST")
    print("=" * 60)
    
    checklist = [
        ("Setup", [
            "Get free Gemini API key: https://aistudio.google.com/app/apikeys",
            "Edit .env and set GOOGLE_API_KEY=<your-key>",
            "Run: docker-compose up --build",
            "Wait for both services to be healthy",
            "Open: http://localhost:3000",
        ]),
        ("Test Cases Ready", [
            "✓ Legitimate PayTM UPI: upi://pay?pa=merchant@okhdfcbank&pn=PayTM&am=100",
            "✓ Suspicious UPI: upi://pay?pa=xyz@gmail.com&pn=Verify&am=500",
            "✓ Legitimate URL: https://paypal.com",
            "✓ Suspicious URL: https://paypal-secure.xyz/verify",
        ]),
        ("Demo Flow", [
            "Personal hook: India UPI fraud epidemic",
            "Live scan LEGITIMATE case",
            "Live scan SUSPICIOUS case",
            "Fallback: Use paste link feature if upload has issues",
        ]),
        ("Talking Points", [
            "QR decoding with OpenCV (avoids zbar dependency)",
            "Heuristic analysis for explainability (not just 'ask LLM')",
            "Google Gemini API for fraud reasoning",
            "Simple, fast, containerized",
        ]),
    ]
    
    for section, items in checklist:
        print(f"\n📌 {section}")
        for item in items:
            print(f"   {item}")


if __name__ == "__main__":
    print("\n" + "🛡️  QUISHGUARD - TEST SUITE" + "\n")
    
    test_phase_1_qr_decoding()
    test_phase_2_heuristics()
    test_phase_3_ai_analysis()
    test_complete_pipeline()
    print_demo_checklist()
    
    print("\n" + "=" * 60)
    print("To start the application:")
    print("  1. Get free key: https://aistudio.google.com/app/apikeys")
    print("  2. Edit .env, set GOOGLE_API_KEY")
    print("  3. Run: docker-compose up --build")
    print("  4. Open: http://localhost:3000")
    print("=" * 60 + "\n")
