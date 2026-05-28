$ python vulnerability_scanner.py https://example.com

======================================================================
🔒 WEB GÜVENLİK ZAFİYET TARAMA TOOL'U
======================================================================
🎯 Hedef: https://example.com
⏰ Başlangıç: 2024-01-15 10:30:45
======================================================================

[2024-01-15 10:30:45] ✅ SQL Injection testi başlıyor...
[2024-01-15 10:30:46] ✅ SQL Injection riski tespit edilmedi
[2024-01-15 10:30:47] ✅ XSS (Cross-Site Scripting) testi başlıyor...
[2024-01-15 10:30:48] ✅ XSS riski tespit edilmedi
...

======================================================================
📊 RAPOR OLUŞTURULUYOR...
======================================================================

📋 TARAMA ÖZETI
----------------------------------------------------------------------
Hedef URL: https://example.com
Tarama Tarihi: 2024-01-15T10:30:45.123456

⚠️  BULUNULAN ZAFİYETLER:
  🔴 KRİTİK: 0
  🟠 YÜKSEK: 2
  🟡 ORTA: 1
  🟢 DÜŞÜK: 1
  📊 TOPLAM: 4

💾 Rapor kaydedildi: security_report.json
