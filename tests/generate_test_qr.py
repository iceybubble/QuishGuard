"""
Generate test QR code images for demo and testing.
Usage: python generate_test_qr.py
Outputs PNG files to tests/qr_images/
"""
import sys
import os

def main():
    try:
        import qrcode
    except ImportError:
        print("Installing qrcode library...")
        os.system(f"{sys.executable} -m pip install qrcode[pil]")
        import qrcode

    output_dir = os.path.join(os.path.dirname(__file__), "qr_images")
    os.makedirs(output_dir, exist_ok=True)

    test_cases = {
        "legitimate_upi.png": {
            "data": "upi://pay?pa=merchant@okhdfcbank&pn=CafeBliss&am=150",
            "desc": "Legitimate UPI - real bank handle, normal merchant name, reasonable amount",
        },
        "legitimate_url.png": {
            "data": "https://paypal.com/checkout",
            "desc": "Legitimate URL - known payment domain, HTTPS",
        },
        "suspicious_url.png": {
            "data": "https://paytm-verify.xyz/secure/login",
            "desc": "Suspicious URL - lookalike domain, suspicious TLD (.xyz)",
        },
        "suspicious_upi.png": {
            "data": "upi://pay?pa=xk29z@gmail.com&pn=Verify&am=999",
            "desc": "Suspicious UPI - random VPA, generic name, non-standard handle",
        },
    }

    print("Generating test QR codes...\n")

    for filename, case in test_cases.items():
        filepath = os.path.join(output_dir, filename)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(case["data"])
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filepath)
        print(f"  ✓ {filename}")
        print(f"    Data: {case['data']}")
        print(f"    Desc: {case['desc']}")
        print()

    print(f"All QR images saved to: {output_dir}")
    print("\nUse these for:")
    print("  1. Testing the /analyze endpoint (upload image)")
    print("  2. Demo day - scan with the app to show live detection")


if __name__ == "__main__":
    main()
