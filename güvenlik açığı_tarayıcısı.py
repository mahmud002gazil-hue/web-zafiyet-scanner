#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Website Güvenlik Zafiyet Bulma Tool'u
Yasal olarak kendi web uygulamalarınızı test etmek için kullanın
"""

import requests
import re
import json
import subprocess
from urllib.parse import urljoin, urlparse
from datetime import datetime
from typing import List, Dict
import time

class WebSecurityScanner:
    """Web uygulaması güvenlik taraması"""
    
    def __init__(self, target_url: str, verbose=False):
        self.target_url = target_url
        self.verbose = verbose
        self.vulnerabilities = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
    
    def log(self, message: str, level="INFO"):
        """Log mesajı yazdır"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        prefix = {
            'INFO': '✅',
            'WARN': '⚠️',
            'ERROR': '❌',
            'VULN': '🔴'
        }.get(level, '📝')
        
        if self.verbose or level != 'INFO':
            print(f"[{timestamp}] {prefix} {message}")
    
    # ===== SQL INJECTION TESTI =====
    def test_sql_injection(self) -> bool:
        """SQL Injection açığını test et"""
        self.log("SQL Injection testi başlıyor...")
        
        payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "admin' --",
            "' UNION SELECT NULL--",
            "1' AND SLEEP(5)--"
        ]
        
        test_params = {'id': '', 'search': '', 'user': '', 'q': ''}
        
        for param_name in test_params.keys():
            for payload in payloads:
                try:
                    params = {param_name: payload}
                    response = self.session.get(
                        self.target_url, 
                        params=params, 
                        headers=self.headers, 
                        timeout=10
                    )
                    
                    # SQL hata mesajlarını kontrol et
                    error_patterns = [
                        r"SQL syntax",
                        r"mysql_fetch",
                        r"Warning: mysql",
                        r"ORA-\d+",
                        r"PostgreSQL"
                    ]
                    
                    for pattern in error_patterns:
                        if re.search(pattern, response.text, re.IGNORECASE):
                            vuln = {
                                'type': 'SQL Injection',
                                'severity': 'CRITICAL',
                                'url': self.target_url,
                                'parameter': param_name,
                                'payload': payload,
                                'evidence': response.text[:200]
                            }
                            self.vulnerabilities.append(vuln)
                            self.log(f"🔴 SQL Injection bulundu! Parameter: {param_name}", "VULN")
                            return True
                
                except Exception as e:
                    self.log(f"SQL test hatası: {e}", "WARN")
        
        self.log("SQL Injection riski tespit edilmedi")
        return False
    
    # ===== XSS (Cross-Site Scripting) TESTI =====
    def test_xss(self) -> bool:
        """XSS açığını test et"""
        self.log("XSS (Cross-Site Scripting) testi başlıyor...")
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src=javascript:alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            try:
                params = {'q': payload, 'search': payload}
                response = self.session.get(
                    self.target_url, 
                    params=params, 
                    headers=self.headers, 
                    timeout=10
                )
                
                # Payload'ın cevapda görünüp görünmediğini kontrol et
                if payload in response.text:
                    vuln = {
                        'type': 'XSS (Cross-Site Scripting)',
                        'severity': 'HIGH',
                        'url': self.target_url,
                        'payload': payload,
                        'reflected': True
                    }
                    self.vulnerabilities.append(vuln)
                    self.log(f"🔴 XSS açığı bulundu!", "VULN")
                    return True
            
            except Exception as e:
                self.log(f"XSS test hatası: {e}", "WARN")
        
        self.log("XSS riski tespit edilmedi")
        return False
    
    # ===== HTTPS/SSL TESTI =====
    def test_ssl_tls(self) -> Dict:
        """SSL/TLS güvenliğini test et"""
        self.log("SSL/TLS testi başlıyor...")
        
        ssl_issues = []
        
        try:
            response = self.session.get(self.target_url, headers=self.headers, timeout=10)
            
            # HTTPS kullanılıyor mu?
            if not self.target_url.startswith('https://'):
                ssl_issues.append({
                    'issue': 'HTTPS kullanılmıyor',
                    'severity': 'HIGH',
                    'recommendation': 'HTTPS etkinleştirin'
                })
                self.log("🔴 HTTPS kullanılmıyor!", "VULN")
            
            # Security Headers kontrolü
            required_headers = {
                'Strict-Transport-Security': 'HSTS',
                'X-Content-Type-Options': 'MIME sniffing koruması',
                'X-Frame-Options': 'Clickjacking koruması',
                'Content-Security-Policy': 'XSS koruması',
                'X-XSS-Protection': 'XSS koruması'
            }
            
            for header, description in required_headers.items():
                if header not in response.headers:
                    ssl_issues.append({
                        'header': header,
                        'description': description,
                        'severity': 'MEDIUM',
                        'status': 'Eksik'
                    })
                    self.log(f"⚠️  {header} header'ı eksik", "WARN")
        
        except Exception as e:
            self.log(f"SSL test hatası: {e}", "WARN")
        
        return ssl_issues
    
    # ===== DIRECTORY TRAVERSAL TESTI =====
    def test_directory_traversal(self) -> bool:
        """Directory Traversal açığını test et"""
        self.log("Directory Traversal testi başlıyor...")
        
        traversal_payloads = [
            "../../../etc/passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd",
            "....//....//....//etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam"
        ]
        
        for payload in traversal_payloads:
            try:
                response = self.session.get(
                    urljoin(self.target_url, payload),
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200 and ('root:' in response.text or '[boot loader]' in response.text):
                    vuln = {
                        'type': 'Directory Traversal',
                        'severity': 'CRITICAL',
                        'payload': payload,
                        'status_code': response.status_code
                    }
                    self.vulnerabilities.append(vuln)
                    self.log("🔴 Directory Traversal açığı bulundu!", "VULN")
                    return True
            
            except Exception as e:
                pass
        
        self.log("Directory Traversal riski tespit edilmedi")
        return False
    
    # ===== DEFAULT CREDENTIALS TESTI =====
    def test_default_credentials(self) -> bool:
        """Default kimlik bilgilerini test et"""
        self.log("Default Credentials testi başlıyor...")
        
        default_creds = [
            ('admin', 'admin'),
            ('admin', 'password'),
            ('admin', '123456'),
            ('root', 'root'),
            ('test', 'test')
        ]
        
        for username, password in default_creds:
            try:
                response = self.session.post(
                    urljoin(self.target_url, '/login'),
                    data={'username': username, 'password': password},
                    headers=self.headers,
                    timeout=10
                )
                
                # Başarılı login göstergeleri
                if response.status_code == 200 and ('dashboard' in response.text.lower() or 'logout' in response.text.lower()):
                    vuln = {
                        'type': 'Default Credentials',
                        'severity': 'CRITICAL',
                        'username': username,
                        'password': password
                    }
                    self.vulnerabilities.append(vuln)
                    self.log(f"🔴 Default credentials bulundu: {username}/{password}", "VULN")
                    return True
            
            except Exception as e:
                pass
        
        self.log("Default credentials tespit edilmedi")
        return False
    
    # ===== OPEN REDIRECT TESTI =====
    def test_open_redirect(self) -> bool:
        """Open Redirect açığını test et"""
        self.log("Open Redirect testi başlıyor...")
        
        redirect_payloads = [
            'https://evil.com',
            '//evil.com',
            'http://google.com',
            'javascript:alert(1)'
        ]
        
        for payload in redirect_payloads:
            try:
                params = {'redirect': payload, 'url': payload}
                response = self.session.get(
                    self.target_url,
                    params=params,
                    headers=self.headers,
                    timeout=10,
                    allow_redirects=False
                )
                
                if response.status_code in [301, 302, 303, 307, 308]:
                    location = response.headers.get('Location', '')
                    if payload in location or 'evil.com' in location:
                        vuln = {
                            'type': 'Open Redirect',
                            'severity': 'MEDIUM',
                            'payload': payload,
                            'redirect_location': location
                        }
                        self.vulnerabilities.append(vuln)
                        self.log("🔴 Open Redirect açığı bulundu!", "VULN")
                        return True
            
            except Exception as e:
                pass
        
        self.log("Open Redirect riski tespit edilmedi")
        return False
    
    # ===== CSRF TOKEN TESTI =====
    def test_csrf(self) -> bool:
        """CSRF koruması testi"""
        self.log("CSRF Koruması testi başlıyor...")
        
        try:
            response = self.session.get(self.target_url, headers=self.headers, timeout=10)
            
            csrf_tokens = [
                '_token',
                'csrf_token',
                '__RequestVerificationToken',
                'authenticity_token'
            ]
            
            has_csrf = any(token in response.text for token in csrf_tokens)
            
            if not has_csrf:
                vuln = {
                    'type': 'CSRF Koruması Eksik',
                    'severity': 'MEDIUM',
                    'recommendation': 'CSRF token ekleyin'
                }
                self.vulnerabilities.append(vuln)
                self.log("🔴 CSRF koruması tespit edilmedi!", "VULN")
                return True
            
            self.log("CSRF koruması bulundu")
            return False
        
        except Exception as e:
            self.log(f"CSRF test hatası: {e}", "WARN")
            return False
    
    # ===== INFORMATION DISCLOSURE TESTI =====
    def test_information_disclosure(self) -> List[Dict]:
        """Bilgi açıklanması testi"""
        self.log("Bilgi Açıklanması testi başlıyor...")
        
        disclosure_issues = []
        
        try:
            response = self.session.get(self.target_url, headers=self.headers, timeout=10)
            
            # Server header kontrolü
            if 'Server' in response.headers:
                server = response.headers.get('Server')
                disclosure_issues.append({
                    'type': 'Server Version Disclosure',
                    'severity': 'LOW',
                    'value': server,
                    'recommendation': 'Server header\'ını gizleyin'
                })
                self.log(f"⚠️  Server versiyonu açığa çıkmış: {server}", "WARN")
            
            # X-Powered-By header kontrolü
            if 'X-Powered-By' in response.headers:
                powered_by = response.headers.get('X-Powered-By')
                disclosure_issues.append({
                    'type': 'Technology Disclosure',
                    'severity': 'LOW',
                    'value': powered_by
                })
                self.log(f"⚠️  Teknoloji bilgisi açığa çıkmış: {powered_by}", "WARN")
            
            # HTML yorumlarında sensitif bilgi
            comments = re.findall(r'<!--(.*?)-->', response.text)
            for comment in comments:
                if any(keyword in comment.lower() for keyword in ['password', 'api', 'key', 'token', 'secret']):
                    disclosure_issues.append({
                        'type': 'Sensitif Bilgi HTML Yorumunda',
                        'severity': 'MEDIUM',
                        'comment': comment[:100]
                    })
                    self.log(f"🔴 HTML yorumunda sensitif bilgi: {comment[:50]}", "VULN")
        
        except Exception as e:
            self.log(f"Disclosure test hatası: {e}", "WARN")
        
        return disclosure_issues
    
    # ===== STATUS CODE TESTI =====
    def test_status_codes(self) -> List[Dict]:
        """Status code testi"""
        self.log("Status Code testi başlıyor...")
        
        status_issues = []
        
        dangerous_paths = [
            '/admin',
            '/admin.php',
            '/admin.aspx',
            '/.git',
            '/.env',
            '/config.php',
            '/database.yml',
            '/web.config',
            '/.well-known/security.txt'
        ]
        
        for path in dangerous_paths:
            try:
                response = self.session.get(
                    urljoin(self.target_url, path),
                    headers=self.headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    status_issues.append({
                        'path': path,
                        'status': response.status_code,
                        'severity': 'HIGH',
                        'issue': 'Hassas dosya/klasör erişilebilir'
                    })
                    self.log(f"🔴 Erişilebilir path bulundu: {path}", "VULN")
            
            except Exception as e:
                pass
        
        return status_issues
    
    # ===== FULL SCAN =====
    def full_scan(self):
        """Tüm testleri çalıştır"""
        print("\n" + "="*70)
        print("🔒 WEB GÜVENLİK ZAFİYET TARAMA TOOL'U")
        print("="*70)
        print(f"🎯 Hedef: {self.target_url}")
        print(f"⏰ Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
        
        # Testleri çalıştır
        self.test_sql_injection()
        time.sleep(1)
        
        self.test_xss()
        time.sleep(1)
        
        ssl_issues = self.test_ssl_tls()
        if ssl_issues:
            self.vulnerabilities.extend(ssl_issues)
        time.sleep(1)
        
        self.test_directory_traversal()
        time.sleep(1)
        
        self.test_default_credentials()
        time.sleep(1)
        
        self.test_open_redirect()
        time.sleep(1)
        
        self.test_csrf()
        time.sleep(1)
        
        disclosure_issues = self.test_information_disclosure()
        if disclosure_issues:
            self.vulnerabilities.extend(disclosure_issues)
        time.sleep(1)
        
        status_issues = self.test_status_codes()
        if status_issues:
            self.vulnerabilities.extend(status_issues)
        
        return self.vulnerabilities
    
    # ===== RAPOR OLUŞTUR =====
    def generate_report(self, filename='security_report.json'):
        """Güvenlik raporunu oluştur"""
        print("\n" + "="*70)
        print("📊 RAPOR OLUŞTURULUYOR...")
        print("="*70 + "\n")
        
        # Zafiyetleri önem derecesine göre sırala
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        sorted_vulns = sorted(
            self.vulnerabilities,
            key=lambda x: severity_order.get(x.get('severity', 'LOW'), 4)
        )
        
        report = {
            'tarih': datetime.now().isoformat(),
            'hedef': self.target_url,
            'toplam_zafiyet': len(self.vulnerabilities),
            'kritik': len([v for v in self.vulnerabilities if v.get('severity') == 'CRITICAL']),
            'yuksek': len([v for v in self.vulnerabilities if v.get('severity') == 'HIGH']),
            'orta': len([v for v in self.vulnerabilities if v.get('severity') == 'MEDIUM']),
            'dusuk': len([v for v in self.vulnerabilities if v.get('severity') == 'LOW']),
            'zafiyetler': sorted_vulns
        }
        
        # Özet yazdır
        print(f"📋 TARAMA ÖZETI")
        print("-"*70)
        print(f"Hedef URL: {self.target_url}")
        print(f"Tarama Tarihi: {report['tarih']}")
        print(f"\n⚠️  BULUNULAN ZAFİYETLER:")
        print(f"  🔴 KRİTİK: {report['kritik']}")
        print(f"  🟠 YÜKSEK: {report['yuksek']}")
        print(f"  🟡 ORTA: {report['orta']}")
        print(f"  🟢 DÜŞÜK: {report['dusuk']}")
        print(f"  📊 TOPLAM: {report['toplam_zafiyet']}")
        
        # Detaylı zafiyetler
        if self.vulnerabilities:
            print("\n" + "-"*70)
            print("DETAYLI ZAFİYET LİSTESİ:")
            print("-"*70)
            for i, vuln in enumerate(sorted_vulns, 1):
                print(f"\n{i}. {vuln.get('type', 'Bilinmeyen Zafiyet')}")
                print(f"   Önem Derecesi: {vuln.get('severity', 'N/A')}")
                for key, value in vuln.items():
                    if key not in ['type', 'severity']:
                        print(f"   {key}: {str(value)[:100]}")
        else:
            print("\n✅ Zafiyet tespit edilmedi!")
        
        # JSON'a kaydet
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=4)
        
        print(f"\n💾 Rapor kaydedildi: {filename}")
        print("="*70 + "\n")
        
        return report

# ===== MAIN =====
def main():
    """Ana program"""
    import sys
    
    if len(sys.argv) < 2:
        print("Kullanım: python vulnerability_scanner.py <URL>")
        print("Örnek: python vulnerability_scanner.py https://example.com")
        print("\n⚠️  NOT: Sadece kendi web uygulamalarınızı test edin!")
        sys.exit(1)
    
    target_url = sys.argv[1]
    
    # URL'i doğrula
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url
    
    try:
        scanner = WebSecurityScanner(target_url, verbose=True)
        vulnerabilities = scanner.full_scan()
        scanner.generate_report()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tarama iptal edildi")
    except Exception as e:
        print(f"\n❌ Hata: {e}")

if __name__ == '__main__':
    main()
