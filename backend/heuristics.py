"""
Phase 2: Heuristic Pre-Analysis
Extract structured signals before sending to LLM - makes verdicts explainable
"""
import re
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Any

class HeuristicAnalyzer:
    """Analyze decoded QR content for fraud signals"""
    
    # Common legitimate payment app schemes
    PAYMENT_SCHEMES = {
        'upi': ['upi://'],
        'gpay': ['tez://'],
        'paytm': ['paytmqr://'],
        'phonepe': ['phonepe://'],
    }
    
    # Suspicious TLDs
    SUSPICIOUS_TLDS = {
        '.xyz', '.top', '.tk', '.ml', '.ga', '.cf',
        '.loan', '.date', '.racing', '.work', '.download',
        '.buzz', '.click', '.link', '.info', '.win',
    }
    
    # Known legitimate payment domains
    LEGITIMATE_PAYMENT_DOMAINS = {
        'paytm.com', 'paypal.com', 'razorpay.com',
        'google.com', 'gpay.com', 'phone.google',
        'upi.npci.co.in', 'upi.google.com',
        'phonepe.com', 'bhimupi.org.in',
    }

    # Known legitimate UPI bank handles
    KNOWN_BANK_HANDLES = {
        'okhdfcbank', 'okaxis', 'okicici', 'oksbi', 'ybl',
        'paytm', 'apl', 'freecharge', 'upi', 'ibl',
        'axl', 'sbi', 'icici', 'hdfcbank', 'axisbank',
        'kotak', 'indus', 'boi', 'pnb', 'unionbank',
        'cbin', 'cnrb', 'idbi', 'rbl', 'federal',
        'kvb', 'dlb', 'kbl', 'mahb', 'aubank',
        'jupiteraxis', 'slice', 'fam',
    }

    # URL shorteners (including Indian-popular ones)
    URL_SHORTENERS = {
        'bit.ly', 'tinyurl.com', 'ow.ly', 'goo.gl', 'short.link',
        't.co', 'cutt.ly', 'is.gd', 'rb.gy', 'shorturl.at',
        'tiny.cc', 'surl.li', 'clck.ru',
    }
    
    def analyze(self, decoded_content: str) -> Dict[str, Any]:
        """
        Analyze decoded QR content for fraud signals.
        
        Args:
            decoded_content: Raw decoded string from QR
            
        Returns:
            Dict with type, signals, and structured data
        """
        result = {
            'raw_value': decoded_content,
            'type': self._detect_type(decoded_content),
            'extracted_signals': [],
            'structured_data': {},
        }
        
        if result['type'] == 'upi':
            result['structured_data'] = self._analyze_upi(decoded_content)
            result['extracted_signals'] = self._check_upi_signals(result['structured_data'])
        elif result['type'] == 'url':
            result['structured_data'] = self._analyze_url(decoded_content)
            result['extracted_signals'] = self._check_url_signals(result['structured_data'])
        elif result['type'] == 'payment_app':
            result['extracted_signals'] = [
                f"Payment app deep link detected: {decoded_content[:40]}...",
                "Verify the app name matches what you expect before proceeding",
            ]
        else:
            result['extracted_signals'] = [
                "Unknown content type - cannot automatically classify"
            ]
        
        return result
    
    def _detect_type(self, content: str) -> str:
        """Detect if content is UPI link, URL, payment app link, or other"""
        lower = content.lower()
        if lower.startswith('upi://'):
            return 'upi'
        elif lower.startswith('tez://') or lower.startswith('phonepe://') or lower.startswith('paytmqr://'):
            return 'payment_app'
        elif lower.startswith('http://') or lower.startswith('https://'):
            return 'url'
        else:
            return 'unknown'
    
    def _analyze_upi(self, upi_string: str) -> Dict[str, Any]:
        """Parse UPI deep link and extract components"""
        try:
            # UPI format: upi://pay?pa=<vpa>&pn=<name>&am=<amount>&...
            parsed = parse_qs(urlparse(upi_string).query)
            
            return {
                'vpa': parsed.get('pa', [None])[0],  # Virtual Payment Address
                'payee_name': parsed.get('pn', [None])[0],
                'amount': parsed.get('am', [None])[0],
                'transaction_ref': parsed.get('tr', [None])[0],
            }
        except Exception as e:
            print(f"Error parsing UPI: {e}")
            return {'error': str(e)}
    
    def _analyze_url(self, url: str) -> Dict[str, Any]:
        """Parse URL and extract domain, path, scheme"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Extract TLD
            tld = self._extract_tld(domain)
            
            return {
                'domain': domain,
                'scheme': parsed.scheme,
                'path': parsed.path,
                'query': parsed.query,
                'tld': tld,
                'is_ip_domain': self._is_ip_address(domain),
                'is_shortener': self._is_url_shortener(domain),
            }
        except Exception as e:
            print(f"Error parsing URL: {e}")
            return {'error': str(e)}
    
    def _check_upi_signals(self, upi_data: Dict[str, Any]) -> List[str]:
        """Check for fraud signals in UPI link"""
        signals = []
        
        if 'error' in upi_data:
            signals.append("Could not parse UPI link")
            return signals
        
        vpa = upi_data.get('vpa', '') or ''
        payee_name = upi_data.get('payee_name', '') or ''
        amount = upi_data.get('amount', '') or ''
        
        # Check for generic/suspicious payee names
        generic_names = ['merchant', 'business', 'service', 'admin', 'support', 'verify', 'refund', 'cashback']
        if payee_name and any(generic in payee_name.lower() for generic in generic_names):
            signals.append(f"Generic payee name: '{payee_name}'")
        
        # Check for suspiciously formatted VPA (random looking)
        if vpa and self._looks_random(vpa.split('@')[0] if '@' in vpa else vpa):
            signals.append(f"VPA looks randomized: '{vpa}'")
        
        # Check VPA handle against known banks
        if vpa and '@' in vpa:
            handle = vpa.split('@')[1]
            if handle not in self.KNOWN_BANK_HANDLES:
                signals.append(f"VPA uses non-standard bank handle: '@{handle}'")
        
        # Check for unusually high amounts
        try:
            if amount and float(amount) > 5000:
                signals.append(f"High payment amount: ₹{amount}")
        except ValueError:
            pass
        
        if not signals:
            signals.append("UPI link structure appears standard")
        
        return signals
    
    def _check_url_signals(self, url_data: Dict[str, Any]) -> List[str]:
        """Check for fraud signals in URL"""
        signals = []
        
        if 'error' in url_data:
            signals.append("Could not parse URL")
            return signals
        
        domain = url_data.get('domain', '')
        
        # Check for HTTP (not HTTPS)
        if url_data.get('scheme') == 'http':
            signals.append("Insecure HTTP connection (no encryption)")
        
        # Check for IP address as domain
        if url_data.get('is_ip_domain'):
            signals.append(f"Direct IP address instead of domain: {domain}")
        
        # Check for suspicious TLD
        tld = url_data.get('tld', '')
        if any(domain.endswith(stld) for stld in self.SUSPICIOUS_TLDS):
            signals.append(f"Suspicious TLD: {tld}")
        
        # Check for lookalike domains (simple heuristic)
        if self._looks_like_lookalike(domain):
            signals.append(f"Domain may be lookalike: '{domain}'")
        
        # Check for URL shortener
        if url_data.get('is_shortener'):
            signals.append(f"URL shortener used: {domain} (obscures actual destination)")
        
        # Check against legitimate list
        base_domain = '.'.join(domain.split('.')[-2:])  # Get base domain
        if base_domain not in self.LEGITIMATE_PAYMENT_DOMAINS and 'payment' in domain.lower():
            signals.append(f"Payment-related domain not in trusted list: '{domain}'")
        
        # Check for excessive subdomains (e.g. secure.login.paytm.fake.xyz)
        subdomain_count = len(domain.split('.')) - 2
        if subdomain_count >= 3:
            signals.append(f"Excessive subdomains ({subdomain_count}) — may be masking real domain")
        
        if not signals:
            signals.append("URL structure appears normal")
        
        return signals
    
    def _extract_tld(self, domain: str) -> str:
        """Extract TLD from domain"""
        parts = domain.split('.')
        if len(parts) >= 2:
            return '.' + parts[-1]
        return ''
    
    def _is_ip_address(self, domain: str) -> bool:
        """Check if domain is an IP address"""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        return bool(re.match(pattern, domain))
    
    def _is_url_shortener(self, domain: str) -> bool:
        """Check if domain is a known URL shortener"""
        return domain in self.URL_SHORTENERS
    
    def _looks_random(self, text: str) -> bool:
        """Heuristic: does text look randomly generated (high entropy)"""
        if not text or len(text) < 4:
            return False
        
        letter_count = sum(1 for c in text if c.isalpha())
        digit_count = sum(1 for c in text if c.isdigit())
        total = letter_count + digit_count
        
        if total == 0:
            return False
        
        # Random-looking if digits dominate (>60% of alphanumeric chars)
        # and the string is reasonably long
        return digit_count > total * 0.6 and total >= 6
    
    def _looks_like_lookalike(self, domain: str) -> bool:
        """Heuristic: domain might be a lookalike of legitimate service"""
        suspicious_patterns = [
            r'paytm.*verify',
            r'paytm.*pay',
            r'paytm-',
            r'phonepe-',
            r'gpay-',
            r'.*-secure\.',
            r'.*-verify\.',
            r'.*-login\.',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, domain, re.IGNORECASE):
                return True
        
        return False


if __name__ == "__main__":
    analyzer = HeuristicAnalyzer()
    
    # Test UPI
    test_upi = "upi://pay?pa=merchant@okhdfcbank&pn=TestShop&am=100"
    result = analyzer.analyze(test_upi)
    print("UPI Analysis:")
    print(result)
    print()
    
    # Test URL
    test_url = "https://paytm-verify.xyz/secure/login"
    result = analyzer.analyze(test_url)
    print("URL Analysis:")
    print(result)
