"""Verify heuristics produce expected signals"""
import sys
sys.path.insert(0, 'backend')
from heuristics import HeuristicAnalyzer

analyzer = HeuristicAnalyzer()

cases = [
    ("upi://pay?pa=merchant@okhdfcbank&pn=CafeBliss&am=150", "Legit UPI"),
    ("upi://pay?pa=xk29z@gmail.com&pn=Verify&am=999", "Suspicious UPI"),
    ("https://paypal.com/checkout", "Legit URL"),
    ("https://paytm-verify.xyz/secure/login", "Suspicious URL"),
]

for content, label in cases:
    result = analyzer.analyze(content)
    print(f"[{label}] type={result['type']}")
    for sig in result['extracted_signals']:
        print(f"  - {sig}")
    print()
