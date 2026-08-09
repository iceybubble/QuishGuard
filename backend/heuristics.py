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
    }
    
    # Suspicious TLDs
    SUSPICIOUS_TLDS = {
        '.xyz', '.top', '.tk', '.ml', '.ga', '.cf',
        '.loan', '.date', '.racing', '.work', '.download',
    }
    
    # Known legitimate payment domains
    LEGITIMATE_PAYMENT_DOMAINS = {
        'paytm.com', 'paypal.com', 'razorpay.com',
        'google.com', 'gpay.com', 'phone.google',
        'upi.npci.co.in', 'upi.google.com',
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
        else:
            result['extracted_signals'] = [
                "Unknown content type - cannot automatically classify"
            ]
        
        return result
    
    def _detect_type(self, content: str) -> str:
        """Detect if content is UPI link, URL, or other"""
        if content.startswith('upi://'):
            return 'upi'
        elif content.startswith('http://') or content.startswith('https://'):
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
        
        vpa = upi_data.get('vpa', '')
        payee_name = upi_data.get('payee_name', '')
        
        # Check for generic/suspicious payee names
        generic_names = ['merchant', 'business', 'service', 'admin', 'support', 'verify']
        if payee_name and any(generic in payee_name.lower() for generic in generic_names):
            signals.append(f"Generic payee name: '{payee_name}'")
        
        # Check for suspiciously formatted VPA (random looking)
        if vpa and self._looks_random(vpa):
            signals.append(f"VPA looks randomized: '{vpa}'")
        
        # Check for known suspicious VPA patterns
        if vpa and not any(vpa.endswith(f'@{bank}') for bank in ['okhdfcbank', 'okaxis', 'okicici', 'oksbi', 'ybl']):
            signals.append(f"VPA uses non-standard bank handle: '{vpa}'")
        
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
        shorteners = {'bit.ly', 'tinyurl.com', 'ow.ly', 'goo.gl', 'short.link'}
        return domain in shorteners or any(domain.startswith(s.split('.')[0]) for s in shorteners)
    
    def _looks_random(self, text: str) -> bool:
        """Heuristic: does text look randomly generated (high entropy)"""
        # Very simple: mostly numbers/consonants without pattern
        letter_count = sum(1 for c in text if c.isalpha())
        digit_count = sum(1 for c in text if c.isdigit())
        
        # Random-looking if mostly digits or weird character mix
        return digit_count > letter_count * 0.5
    
    def _looks_like_lookalike(self, domain: str) -> bool:
        """Heuristic: domain might be a lookalike of legitimate service"""
        suspicious_patterns = [
            r'paytm.*verify',
            r'paytm.*pay',
            r'.*paypal.*',
            r'.*bank.*',
            r'.*verify.*',
            r'.*secure.*',
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
