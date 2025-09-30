# Makine Çeviri - Dosya Çeviricisi

Modern bir masaüstü uygulaması ile dosya çeviri işlemlerini kolaylaştırın.

## Özellikler

- 🗂️ **Klasör Tabanlı Dosya Yönetimi**: Windows Explorer benzeri dosya ağacı görünümü
- 📄 **Çoklu Format Desteği**: TXT, JSON, XML, INI, CFG, Properties, Lang, YML, YAML dosyaları
- 🎨 **Modern Arayüz**: Dark/Light tema desteği ile modern CustomTkinter tasarımı
- 🧭 **Akıllı Klasör Gezinme**: Klasör durum kartları ve tek tıkla kılavuz/günlük kısayolları
- � **Anlık Arama**: Dosya ağacında yazarken filtreleme ve eşleşmeleri vurgulama
- �🔄 **Anlık Çeviri**: Seçilen dosyaların anlık çevirisi
- 📊 **Canlı İstatistikler**: Orijinal ve çevrilmiş içerik için satır/karakter sayacı
- 📋 **Tek Tıkla Kopyalama**: Orijinal veya çevrilmiş metni panoya aktarma
- 📤 **Toplu Dışa Aktarma**: Çevrilmiş dosyaları tek seferde dışa aktarma
- ✅ **Seçici İşlem**: Checkbox ile istediğiniz dosyaları seçerek işlem yapma

## Kurulum

1. Python 3.8+ gerekli
2. Gerekli paketleri yükleyin:

```bash
pip install -r requirements.txt
```

## Kullanım

```bash
python main.py
```

### Adım Adım Kullanım:

1. **Klasör Seç**: Sol panelden "Klasör Seç" butonuna tıklayarak çevirmek istediğiniz dosyaları içeren klasörü seçin
2. **Dosya Seç veya Ara**: Dosya ağacından çevirmek istediğiniz dosyaya tıklayın ya da üstteki arama alanıyla doğrudan filtreleyin (desteklenen formatlar yeşil renkle gösterilir)
3. **İçeriği İncele**: Orta panelde dosyanın orijinal içeriği görüntülenir
4. **Çevir**: "Çevir" butonuna tıklayarak çeviri işlemini başlatın
5. **Sonucu Görüntüle**: Sağ panelde çevrilmiş içerik görüntülenir
6. **Dışa Aktar**: "Dışa Aktar" butonu ile çevrilmiş dosyaları kaydedin

## Desteklenen Dosya Formatları

- `.txt` - Metin dosyaları
- `.json` - JSON veri dosyaları
- `.xml` - XML dosyaları
- `.ini` - Konfigürasyon dosyaları
- `.cfg` - Ayar dosyaları
- `.properties` - Properties dosyaları
- `.lang` - Dil dosyaları
- `.yml`, `.yaml` - YAML dosyaları

## Teknik Detaylar

### Kullanılan Teknolojiler:
- **CustomTkinter**: Modern UI framework
- **tkinter.ttk**: TreeView komponenti için
- **chardet**: Dosya kodlama algılama
- **pathlib**: Dosya yolu işlemleri
- **threading**: Asenkron işlemler

### Proje Yapısı:
```
frontend/
├── main.py              # Ana uygulama
├── requirements.txt     # Python bağımlılıkları
└── README.md           # Bu dosya
```

## Özelleştirme

### Tema Değiştirme:
Uygulama alt kısmındaki "Dark/Light" switch'i ile tema değiştirilebilir.

### Yeni Format Ekleme:
`main.py` dosyasındaki `supported_formats` listesine yeni dosya uzantıları ekleyebilirsiniz:

```python
self.supported_formats = ['.txt', '.json', '.xml', '.ini', '.cfg', '.properties', '.lang', '.yml', '.yaml', '.yeni_format']
```

## Gelecek Özellikler

- [ ] Gerçek çeviri API entegrasyonu (Google Translate, Azure Translator, vb.)
- [ ] Çoklu dil desteği
- [ ] Dosya önizleme
- [ ] Çeviri geçmişi
- [ ] Batch işlem modu
- [ ] Çeviri kalitesi analizi
- [ ] Sürükle-bırak dosya desteği

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.
