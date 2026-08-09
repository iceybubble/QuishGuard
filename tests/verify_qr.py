"""Quick verification: decode all test QR images and check results"""
import sys
sys.path.insert(0, 'backend')
from qr_decoder import QRDecoder

decoder = QRDecoder()
tests = {
    'tests/qr_images/legitimate_upi.png': 'upi://pay?pa=merchant@okhdfcbank&pn=CafeBliss&am=150',
    'tests/qr_images/legitimate_url.png': 'https://paypal.com/checkout',
    'tests/qr_images/suspicious_url.png': 'https://paytm-verify.xyz/secure/login',
    'tests/qr_images/suspicious_upi.png': 'upi://pay?pa=xk29z@gmail.com&pn=Verify&am=999',
}

all_ok = True
for path, expected in tests.items():
    result = decoder.decode_from_file(path)
    ok = (result == expected)
    if not ok:
        all_ok = False
    status = "PASS" if ok else "FAIL"
    print(f"{status}: {path.split('/')[-1]}")
    if not ok:
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")

print()
if all_ok:
    print("ALL QR DECODE TESTS PASSED")
else:
    print("SOME TESTS FAILED")
    sys.exit(1)
