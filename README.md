# 🔒 Web Güvenlik Zafiyet Bulma Tool'u

Website güvenlik açıklarını (zafiyetleri) otomatik olarak tarayıp tespit eden Python aracı.

## ⚠️ UYARI

**YASAL UYARI:** Bu tool sadece **kendi web uygulamalarınızı** test etmek için kullanılmalıdır. 
İzinsiz olarak başka siteleri taramak **YASADIŞıDIR** ve yasal sonuçlara yol açabilir.

## 🎯 Özellikler

Tarama aracı aşağıdaki güvenlik açıklarını tespit eder:

- 🔴 **SQL Injection** - SQL injection açıkları
- 🔴 **XSS (Cross-Site Scripting)** - XSS açıkları
- 🔴 **Directory Traversal** - Dosya erişim açıkları
- 🔴 **Default Credentials** - Varsayılan şifreler
- 🟠 **HTTPS/SSL Kontrolü** - SSL/TLS ve security header'ları
- 🟠 **Open Redirect** - Redirect açıkları
- 🟡 **CSRF Koruması** - CSRF token kontrolü
- 🟡 **Information Disclosure** - Bilgi açıklanması
- 🟡 **Status Code Analizi** - Hassas dosyaların erişilebilirliği

## 📋 Gereksinimler

- Python 3.7+
- pip paket yöneticisi

## 🚀 Kurulum

### 1. Repository'yi klonla
```bash
git clone https://github.com/mahmud002gazil-hue/web-zafiyet-scanner.git
cd web-zafiyet-scanner
