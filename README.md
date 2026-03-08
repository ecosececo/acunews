# 🎓 ACU NEWS - Acıbadem Üniversitesi Haber Portalı

<p align="center">
  <img src="static/images/logo.svg" alt="ACU NEWS Logo" width="400">
</p>

<p align="center">
  <strong>Modern, AR/VR efektli ve kullanıcı dostu bir üniversite haber portalı</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.0-green?logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap" alt="Bootstrap">
  <img src="https://img.shields.io/badge/Three.js-3D-black?logo=three.js" alt="Three.js">
</p>

---

## ✨ Özellikler

### 📰 Haber Yönetimi
- Haber ekleme, düzenleme ve silme
- Kategorilere göre haber filtreleme (Akademik, Sosyal, Spor, Duyurular, Etkinlikler)
- Görsel yükleme desteği (PNG, JPG, GIF, WebP)
- Haber arama fonksiyonu
- Okunma sayısı takibi

### 👤 Kullanıcı Sistemi
- Üye olma ve giriş yapma
- Profil yönetimi ve düzenleme
- Profil fotoğrafı yükleme
- Şifre değiştirme
- Bölüm seçimi (Tıp, Diş Hekimliği, Eczacılık, Sağlık Bilimleri, vb.)

### 🎨 Modern Tasarım
- **AR/VR Efektleri**: Three.js ile 3D arka plan animasyonları
- **Neon Glow**: Parlayan butonlar ve kartlar
- **Glassmorphism**: Cam efektli UI bileşenleri
- **Parçacık Animasyonları**: Yüzen parçacıklar ve şekiller
- **GSAP Animasyonları**: Akıcı geçişler ve hover efektleri
- **Responsive Tasarım**: Mobil uyumlu arayüz

### 🔐 Güvenlik
- Şifre hashleme (Werkzeug)
- Flask-Login ile oturum yönetimi
- CSRF koruması
- Güvenli dosya yükleme

---

## 🚀 Kurulum

### Gereksinimler
- Python 3.10+
- pip

### Adımlar

1. **Repoyu klonlayın:**
```bash
git clone https://github.com/ecosececo/acunews.git
cd acunews
```

2. **Sanal ortam oluşturun:**
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# veya
venv\Scripts\activate  # Windows
```

3. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

4. **Uygulamayı başlatın:**
```bash
python app.py
```

5. **Tarayıcıda açın:**
```
http://127.0.0.1:5000
```

---

## 📁 Proje Yapısı

```
acunews/
├── app.py                 # Ana Flask uygulaması
├── requirements.txt       # Python bağımlılıkları
├── haberler.db           # SQLite veritabanı (otomatik oluşur)
├── static/
│   ├── images/
│   │   ├── logo.svg      # ACU NEWS logosu
│   │   └── favicon.svg   # Favicon
│   └── uploads/          # Yüklenen görseller
└── templates/
    ├── base.html         # Ana şablon (AR/VR efektleri)
    ├── ana_sayfa.html    # Ana sayfa
    ├── giris.html        # Giriş sayfası
    ├── uye_ol.html       # Üye olma sayfası
    ├── profil.html       # Profil sayfası
    ├── profil_duzenle.html
    ├── haber_ekle.html   # Haber ekleme
    ├── haber_detay.html  # Haber detay
    ├── haber_duzenle.html
    ├── kategori.html     # Kategori sayfası
    ├── arama.html        # Arama sonuçları
    └── hakkinda.html     # Hakkında sayfası
```

---

## 🛠️ Teknolojiler

| Teknoloji | Kullanım |
|-----------|----------|
| **Flask** | Web framework |
| **SQLAlchemy** | ORM & Veritabanı |
| **Flask-Login** | Kullanıcı oturumları |
| **SQLite** | Veritabanı |
| **Bootstrap 5** | UI framework |
| **Three.js** | 3D grafikler |
| **GSAP** | Animasyonlar |
| **Font Awesome** | İkonlar |

---

## 👥 Varsayılan Admin Hesabı

Uygulama ilk çalıştırıldığında otomatik olarak bir admin hesabı oluşturulur:

- **Email:** `admin@acibadem.edu.tr`
- **Şifre:** `admin123`

> ⚠️ Güvenlik için bu şifreyi değiştirmeniz önerilir.

---

## 📸 Ekran Görüntüleri

### Ana Sayfa
- Modern neon tasarım
- Kategori filtreleme
- Son haberler listesi

### Haber Detay
- Görsel banner
- Yazar bilgileri
- Okunma sayısı

### Profil Sayfası
- Kullanıcı istatistikleri
- Paylaşılan haberler
- Profil düzenleme

---

## 🎯 Gelecek Özellikler

- [ ] Yorum sistemi
- [ ] Haber beğenme
- [ ] E-posta bildirimleri
- [ ] Sosyal medya paylaşımı
- [ ] Çoklu dil desteği
- [ ] Dark/Light tema

---

## 📄 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

---

## 👩‍💻 Geliştirici

**Ece Eylül Şen**
- GitHub: [@ecosececo](https://github.com/ecosececo)

---

<p align="center">
  
</p>
