Code Analyzer Backend

Bu proje, bitirme projem kapsamında geliştirdiğim AI destekli kod analiz sisteminin backend kısmıdır.

Amaç, kullanıcı tarafından yüklenen kaynak kodları analiz ederek olası hataları tespit etmek ve kodun geliştirilmesine yönelik öneriler sunmaktır. Projede klasik statik analiz yaklaşımı ile yapay zeka destekli analiz birlikte kullanılmaktadır.

Proje Mimarisi

Sistem aşağıdaki adımlardan oluşmaktadır:

Kod Girişi
    ↓
Statik Analiz
    ↓
Kural Tabanlı Kontroller
    ↓
AI Analizi
    ↓
Sonuç Raporu

1. Statik Analiz

İlk aşamada kod temel kontrollerden geçirilir. Sözdizimi hataları ve bazı yapısal problemler tespit edilmeye çalışılır.

2. Kural Tabanlı Analiz

Bu aşamada önceden tanımlanmış kurallar kullanılarak yaygın yazılım hataları ve kötü kodlama pratikleri kontrol edilir.

3. AI Analizi

Statik analiz sonuçları yapay zeka katmanına gönderilir. Bu katman kodu yorumlayarak geliştiriciye açıklamalar ve iyileştirme önerileri sunar.

4. Raporlama

Tüm analiz sonuçları birleştirilerek kullanıcıya tek bir rapor halinde gösterilir.

Kullanılan Teknolojiler

* Python
* FastAPI
* REST API
* Yapay Zeka / LLM Entegrasyonu
* Rule-Based Analiz Yaklaşımı

Geliştirme Amacı

Bu proje, geleneksel statik analiz yöntemleri ile yapay zeka destekli analiz yaklaşımlarını bir araya getirerek geliştiricilere daha anlaşılır geri bildirimler sunmayı amaçlamaktadır.

Gelecek Çalışmalar

* Daha fazla programlama dili desteği eklenmesi
* Lokal LLM entegrasyonu
* Docker desteğinin geliştirilmesi
* CI/CD entegrasyonu
* Daha kapsamlı güvenlik analizleri

Ge
