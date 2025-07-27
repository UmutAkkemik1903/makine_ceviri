# Makine Çeviri Uygulaması - Kullanım Kılavuzu

## 🚀 Hızlı Başlangıç

### Gereksinimler
- Python 3.8 veya üzeri
- Windows işletim sistemi

### Kurulum
1. `requirements.txt` dosyasındaki paketleri yükleyin:
   ```
   pip install -r requirements.txt
   ```

2. Uygulamayı başlatın:
   ```
   python main.py
   ```
   veya
   ```
   run.bat
   ```

## 📋 Arayüz Açıklaması

### Sol Panel - Dosya Seçimi
- **Klasör Seç** butonu ile çevirmek istediğiniz dosyaları içeren klasörü seçin
- Dosya ağacı Windows Explorer benzeri yapıda görüntülenir
- 📁 simgesi: Klasörler
- 📄 simgesi + ✅: Desteklenen dosyalar
- 📋 simgesi + ❌: Desteklenmeyen dosyalar

### Orta Panel - Orijinal İçerik
- Seçilen dosyanın orijinal içeriği burada görüntülenir
- Dosya kodlaması otomatik algılanır
- Türkçe karakterler doğru şekilde gösterilir

### Sağ Panel - Çevrilmiş İçerik  
- Çeviri işlemi sonrası yeni içerik burada görüntülenir
- Format korunarak çeviri yapılır
- Değiştirilen kısımlar "[ÇEVRİLDİ]" etiketi ile işaretlenir

### Alt Panel - Kontroller
- **Tema Switch**: Dark/Light tema geçişi
- **Çevir** butonu: Seçili dosyayı çevirir
- **Tümünü Çevir** checkbox: Tüm desteklenen dosyaları toplu çevirir
- **Dışa Aktar** butonu: Çevrilmiş dosyaları kaydeder
- **Progress Bar**: İşlem ilerlemesini gösterir
- **Durum Etiketi**: Anlık durum bilgisi

## 🔧 Özellik Detayları

### Desteklenen Dosya Formatları
- **.txt**: Düz metin dosyaları
- **.json**: JSON veri dosyaları
- **.xml**: XML belgeleri  
- **.ini**: Konfigürasyon dosyaları
- **.cfg**: Ayar dosyaları
- **.properties**: Properties dosyaları
- **.lang**: Dil dosyaları
- **.yml/.yaml**: YAML dosyaları

### Çeviri Mantığı
- **JSON**: Key-value çiftlerinde sadece value kısmı çevrilir
- **INI/CFG**: = işaretinden sonraki değerler çevrilir
- **Properties**: = işaretinden sonraki değerler çevrilir
- **TXT**: Tüm metin içeriği çevrilir
- **Yorum satırları**: # ile başlayan satırlar korunur

### Toplu İşlem
1. "Tüm desteklenen dosyaları çevir" seçeneğini işaretleyin
2. "Çevir" butonuna tıklayın
3. Seçili klasördeki tüm desteklenen dosyalar otomatik çevrilir
4. Progress bar ile ilerleme takip edilir

### Dışa Aktarma
- Çevrilmiş dosyalar "_translated" eki ile kaydedilir
- Orijinal klasör yapısı korunmaz (tek klasöre kaydedilir)
- Dosya kodlaması UTF-8 olarak ayarlanır

## 🎨 Tema Ayarları

### Dark Tema (Varsayılan)
- Koyu arka plan
- Beyaz/açık gri yazılar
- Mavi vurgu renkleri

### Light Tema  
- Açık arka plan
- Koyu yazılar
- Mavi vurgu renkleri

Tema değişikliği anlık olarak uygulanır.

## 🔍 Sorun Giderme

### Dosya Görüntülenmiyor
- Dosya kodlamasında sorun olabilir
- Desteklenen format olduğundan emin olun
- Dosya izinlerini kontrol edin

### Çeviri Çalışmıyor
- İnternet bağlantısını kontrol edin (gelecek sürümlerde)
- Dosya içeriğinin çok büyük olmadığından emin olun

### Dışa Aktarma Hatası
- Hedef klasöre yazma izni olduğundan emin olun
- Disk alanının yeterli olduğunu kontrol edin

## 🔮 Gelecek Özellikler

- Google Translate API entegrasyonu
- Çoklu dil desteği (Türkçe ↔ İngilizce, vb.)
- Çeviri geçmişi
- Dosya önizleme
- Sürükle-bırak desteği
- Çeviri kalitesi değerlendirmesi

## 📞 Destek

Sorunlar için:
1. README.md dosyasını inceleyin
2. Test dosyaları ile deneyin
3. Konsol çıktısını kontrol edin
