#!/usr/bin/env python3
"""
QuishGuard Quick Start Guide
Run this to see setup instructions and verify your environment
"""

def print_banner():
    print("\n" + "=" * 70)
    print("🛡️  QUISHGUARD - QR Code Security Scanner")
    print("=" * 70 + "\n")


def print_setup_instructions():
    print("📋 SETUP INSTRUCTIONS (5 minutes)\n")
    
    steps = [
        ("1. Get FREE API Key", [
            "Visit: https://aistudio.google.com/app/apikeys",
            "Sign in with Google (create account if needed)",
            "Click 'Create API Key'",
            "Copy the key (no billing required!)",
        ]),
        ("2. Configure Environment", [
            "Edit: .env file in QuishGuard folder",
            'Set: GOOGLE_API_KEY="your-key-here"',
            "Save the file",
        ]),
        ("3. Start Application", [
            "Windows: Run start.bat",
            "Mac/Linux: bash start.sh",
            "Or manually: docker-compose up",
            "Wait for both services to start (~30 seconds)",
        ]),
        ("4. Open Browser", [
            "Frontend: http://localhost:3000",
            "Backend: http://localhost:8000",
            "Health: curl http://localhost:8000/health",
        ]),
    ]
    
    for title, items in steps:
        print(f"  {title}")
        for item in items:
            print(f"    • {item}")
        print()


def print_demo_cases():
    print("\n📊 DEMO TEST CASES (copy-paste into app)\n")
    
    cases = [
        ("✅ Legitimate - PayPal", "https://paypal.com", "LOW"),
        ("✅ Legitimate - UPI", "upi://pay?pa=merchant@okhdfcbank&pn=PayTM&am=100", "LOW"),
        ("⚠️  Suspicious - Lookalike", "https://paytm-verify.xyz/secure/login", "HIGH"),
        ("⚠️  Suspicious - UPI Fraud", "upi://pay?pa=randomuser123@gmail.com&pn=Verify&am=500", "MEDIUM"),
    ]
    
    for label, content, risk in cases:
        print(f"  {label}")
        print(f"    Input:    {content}")
        print(f"    Expected: {risk} risk")
        print()


def print_file_structure():
    print("\n📁 PROJECT STRUCTURE\n")
    
    structure = """
    QuishGuard/
    ├── backend/
    │   ├── main.py              ← FastAPI server
    │   ├── qr_decoder.py        ← OpenCV QR decode
    │   ├── heuristics.py        ← Fraud signal detection
    │   ├── ai_analyzer.py       ← Claude integration
    │   ├── requirements.txt
    │   ├── Dockerfile
    │   └── __init__.py
    ├── frontend/
    │   ├── index.html           ← Single-page app
    │   └── Dockerfile
    ├── tests/
    │   ├── manual_test.py       ← Local pipeline test
    │   └── test_demo.py         ← Demo checklist
    ├── docker-compose.yml       ← Orchestration
    ├── .env.example             ← Config template
    ├── start.sh / start.bat     ← Quick start scripts
    └── README.md
    """
    
    print(structure)


def print_demo_flow():
    print("\n🎤 DEMO FLOW (2-3 minutes)\n")
    
    flow = [
        "1. **Hook** - 'Fake QR stickers are everywhere in India'",
        "2. **Live Demo 1** - Paste legitimate link → show LOW risk, green badge",
        "3. **Live Demo 2** - Paste suspicious link → show HIGH risk, red badge",
        "4. **Explain** - Walk through detected signals (domain, TLD, etc.)",
        "5. **Fallback** - Show 'paste link' feature works if upload fails",
        "6. **Close** - 'Before tapping any QR, QuishGuard has your back'",
    ]
    
    for item in flow:
        print(f"  {item}")
    
    print()


def print_troubleshooting():
    print("\n🔧 TROUBLESHOOTING\n")
    
    issues = [
        ("Docker not installed", "Download from docker.com"),
        ("Port 3000/8000 in use", "Change ports in docker-compose.yml"),
        ("ANTHROPIC_API_KEY error", "Check .env file exists and has valid key"),
        ("QR not detected", "Image must be clear, 50x50px minimum - use paste tab"),
        ("Containers won't start", "Run: docker-compose down && docker-compose up --build"),
    ]
    
    for issue, solution in issues:
        print(f"  ❌ {issue}")
        print(f"     ✓ {solution}\n")


def main():
    print_banner()
    print_setup_instructions()
    print_demo_cases()
    print_file_structure()
    print_demo_flow()
    print_troubleshooting()
    
    print("=" * 70)
    print("🚀 Ready to build? Follow the setup instructions above!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
