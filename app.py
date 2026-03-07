from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'universite-haber-secret-key'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'haberler.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Dosya yükleme ayarları
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Upload klasörünü oluştur
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'giris'
login_manager.login_message = 'Bu sayfaya erişmek için giriş yapmalısınız.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return Kullanici.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    if file and allowed_file(file.filename):
        # Benzersiz dosya adı oluştur
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename
    return None

# Veritabanı Modelleri
class Kullanici(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False)
    soyad = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    sifre_hash = db.Column(db.String(256), nullable=False)
    ogrenci_no = db.Column(db.String(20), unique=True)
    bolum = db.Column(db.String(100))
    profil_resmi = db.Column(db.String(500))
    rol = db.Column(db.String(20), default='ogrenci')  # admin, ogrenci, ogretim_uyesi
    kayit_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    aktif = db.Column(db.Boolean, default=True)
    haberler = db.relationship('Haber', backref='yazar_kullanici', lazy=True)
    
    def set_password(self, sifre):
        self.sifre_hash = generate_password_hash(sifre)
    
    def check_password(self, sifre):
        return check_password_hash(self.sifre_hash, sifre)

class Kategori(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(50), nullable=False)
    haberler = db.relationship('Haber', backref='kategori', lazy=True)

class Haber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(200), nullable=False)
    icerik = db.Column(db.Text, nullable=False)
    ozet = db.Column(db.String(500))
    yazar = db.Column(db.String(100), default='Admin')
    yazar_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'))
    gorsel_url = db.Column(db.String(500))
    tarih = db.Column(db.DateTime, default=datetime.utcnow)
    kategori_id = db.Column(db.Integer, db.ForeignKey('kategori.id'), nullable=False)
    okunma_sayisi = db.Column(db.Integer, default=0)

# Ana Sayfa
@app.route('/')
def ana_sayfa():
    haberler = Haber.query.order_by(Haber.tarih.desc()).all()
    kategoriler = Kategori.query.all()
    return render_template('ana_sayfa.html', haberler=haberler, kategoriler=kategoriler)

# Kategori Sayfası
@app.route('/kategori/<int:kategori_id>')
def kategori_sayfasi(kategori_id):
    kategori = Kategori.query.get_or_404(kategori_id)
    haberler = Haber.query.filter_by(kategori_id=kategori_id).order_by(Haber.tarih.desc()).all()
    kategoriler = Kategori.query.all()
    return render_template('kategori.html', kategori=kategori, haberler=haberler, kategoriler=kategoriler)

# Haber Detay
@app.route('/haber/<int:haber_id>')
def haber_detay(haber_id):
    haber = Haber.query.get_or_404(haber_id)
    haber.okunma_sayisi += 1
    db.session.commit()
    kategoriler = Kategori.query.all()
    return render_template('haber_detay.html', haber=haber, kategoriler=kategoriler)

# Haber Ekle
@app.route('/haber-ekle', methods=['GET', 'POST'])
def haber_ekle():
    kategoriler = Kategori.query.all()
    if request.method == 'POST':
        baslik = request.form['baslik']
        icerik = request.form['icerik']
        ozet = request.form['ozet']
        yazar = request.form['yazar']
        kategori_id = request.form['kategori_id']
        
        # Görsel yükleme
        gorsel_url = None
        if 'gorsel' in request.files:
            file = request.files['gorsel']
            if file and file.filename:
                filename = save_image(file)
                if filename:
                    gorsel_url = filename
        
        yeni_haber = Haber(
            baslik=baslik,
            icerik=icerik,
            ozet=ozet,
            yazar=yazar,
            gorsel_url=gorsel_url,
            kategori_id=kategori_id
        )
        
        db.session.add(yeni_haber)
        db.session.commit()
        flash('Haber başarıyla eklendi!', 'success')
        return redirect(url_for('ana_sayfa'))
    
    return render_template('haber_ekle.html', kategoriler=kategoriler)

# Haber Düzenle
@app.route('/haber-duzenle/<int:haber_id>', methods=['GET', 'POST'])
def haber_duzenle(haber_id):
    haber = Haber.query.get_or_404(haber_id)
    kategoriler = Kategori.query.all()
    
    if request.method == 'POST':
        haber.baslik = request.form['baslik']
        haber.icerik = request.form['icerik']
        haber.ozet = request.form['ozet']
        haber.yazar = request.form['yazar']
        haber.kategori_id = request.form['kategori_id']
        
        # Yeni görsel yüklendiyse güncelle
        if 'gorsel' in request.files:
            file = request.files['gorsel']
            if file and file.filename:
                # Eski görseli sil
                if haber.gorsel_url and not haber.gorsel_url.startswith('http'):
                    eski_gorsel = os.path.join(app.config['UPLOAD_FOLDER'], haber.gorsel_url)
                    if os.path.exists(eski_gorsel):
                        os.remove(eski_gorsel)
                
                filename = save_image(file)
                if filename:
                    haber.gorsel_url = filename
        
        db.session.commit()
        flash('Haber başarıyla güncellendi!', 'success')
        return redirect(url_for('haber_detay', haber_id=haber.id))
    
    return render_template('haber_duzenle.html', haber=haber, kategoriler=kategoriler)

# Haber Sil
@app.route('/haber-sil/<int:haber_id>')
def haber_sil(haber_id):
    haber = Haber.query.get_or_404(haber_id)
    
    # Görseli sil
    if haber.gorsel_url and not haber.gorsel_url.startswith('http'):
        gorsel_path = os.path.join(app.config['UPLOAD_FOLDER'], haber.gorsel_url)
        if os.path.exists(gorsel_path):
            os.remove(gorsel_path)
    
    db.session.delete(haber)
    db.session.commit()
    flash('Haber başarıyla silindi!', 'success')
    return redirect(url_for('ana_sayfa'))

# Arama
@app.route('/ara')
def ara():
    sorgu = request.args.get('q', '')
    kategoriler = Kategori.query.all()
    if sorgu:
        haberler = Haber.query.filter(
            (Haber.baslik.contains(sorgu)) | (Haber.icerik.contains(sorgu))
        ).order_by(Haber.tarih.desc()).all()
    else:
        haberler = []
    return render_template('arama.html', haberler=haberler, sorgu=sorgu, kategoriler=kategoriler)

# Hakkında
@app.route('/hakkinda')
def hakkinda():
    kategoriler = Kategori.query.all()
    return render_template('hakkinda.html', kategoriler=kategoriler)

# Giriş Yap
@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if current_user.is_authenticated:
        return redirect(url_for('ana_sayfa'))
    
    kategoriler = Kategori.query.all()
    if request.method == 'POST':
        email = request.form['email']
        sifre = request.form['sifre']
        hatirla = 'hatirla' in request.form
        
        kullanici = Kullanici.query.filter_by(email=email).first()
        
        if kullanici and kullanici.check_password(sifre):
            if not kullanici.aktif:
                flash('Hesabınız devre dışı bırakılmış.', 'danger')
                return redirect(url_for('giris'))
            
            login_user(kullanici, remember=hatirla)
            flash(f'Hoş geldiniz, {kullanici.ad}!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('ana_sayfa'))
        else:
            flash('E-posta veya şifre hatalı!', 'danger')
    
    return render_template('giris.html', kategoriler=kategoriler)

# Üye Ol
@app.route('/uye-ol', methods=['GET', 'POST'])
def uye_ol():
    if current_user.is_authenticated:
        return redirect(url_for('ana_sayfa'))
    
    kategoriler = Kategori.query.all()
    if request.method == 'POST':
        ad = request.form['ad']
        soyad = request.form['soyad']
        email = request.form['email']
        sifre = request.form['sifre']
        sifre_tekrar = request.form['sifre_tekrar']
        ogrenci_no = request.form.get('ogrenci_no', '')
        bolum = request.form.get('bolum', '')
        
        # Validasyonlar
        if sifre != sifre_tekrar:
            flash('Şifreler eşleşmiyor!', 'danger')
            return redirect(url_for('uye_ol'))
        
        if len(sifre) < 6:
            flash('Şifre en az 6 karakter olmalıdır!', 'danger')
            return redirect(url_for('uye_ol'))
        
        if Kullanici.query.filter_by(email=email).first():
            flash('Bu e-posta adresi zaten kayıtlı!', 'danger')
            return redirect(url_for('uye_ol'))
        
        if ogrenci_no and Kullanici.query.filter_by(ogrenci_no=ogrenci_no).first():
            flash('Bu öğrenci numarası zaten kayıtlı!', 'danger')
            return redirect(url_for('uye_ol'))
        
        # Profil resmi yükleme
        profil_resmi = None
        if 'profil_resmi' in request.files:
            file = request.files['profil_resmi']
            if file and file.filename:
                filename = save_image(file)
                if filename:
                    profil_resmi = filename
        
        # Yeni kullanıcı oluştur
        yeni_kullanici = Kullanici(
            ad=ad,
            soyad=soyad,
            email=email,
            ogrenci_no=ogrenci_no if ogrenci_no else None,
            bolum=bolum if bolum else None,
            profil_resmi=profil_resmi,
            rol='ogrenci'
        )
        yeni_kullanici.set_password(sifre)
        
        db.session.add(yeni_kullanici)
        db.session.commit()
        
        flash('Kayıt başarılı! Şimdi giriş yapabilirsiniz.', 'success')
        return redirect(url_for('giris'))
    
    return render_template('uye_ol.html', kategoriler=kategoriler)

# Çıkış Yap
@app.route('/cikis')
@login_required
def cikis():
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('ana_sayfa'))

# Profil
@app.route('/profil')
@login_required
def profil():
    kategoriler = Kategori.query.all()
    kullanici_haberleri = Haber.query.filter_by(yazar_id=current_user.id).order_by(Haber.tarih.desc()).all()
    return render_template('profil.html', kategoriler=kategoriler, haberler=kullanici_haberleri)

# Profil Düzenle
@app.route('/profil-duzenle', methods=['GET', 'POST'])
@login_required
def profil_duzenle():
    kategoriler = Kategori.query.all()
    
    if request.method == 'POST':
        current_user.ad = request.form['ad']
        current_user.soyad = request.form['soyad']
        current_user.bolum = request.form.get('bolum', '')
        
        # Şifre değiştirme
        eski_sifre = request.form.get('eski_sifre', '')
        yeni_sifre = request.form.get('yeni_sifre', '')
        yeni_sifre_tekrar = request.form.get('yeni_sifre_tekrar', '')
        
        if eski_sifre and yeni_sifre:
            if not current_user.check_password(eski_sifre):
                flash('Mevcut şifre hatalı!', 'danger')
                return redirect(url_for('profil_duzenle'))
            
            if yeni_sifre != yeni_sifre_tekrar:
                flash('Yeni şifreler eşleşmiyor!', 'danger')
                return redirect(url_for('profil_duzenle'))
            
            if len(yeni_sifre) < 6:
                flash('Yeni şifre en az 6 karakter olmalıdır!', 'danger')
                return redirect(url_for('profil_duzenle'))
            
            current_user.set_password(yeni_sifre)
        
        # Profil resmi güncelleme
        if 'profil_resmi' in request.files:
            file = request.files['profil_resmi']
            if file and file.filename:
                # Eski resmi sil
                if current_user.profil_resmi:
                    eski_resim = os.path.join(app.config['UPLOAD_FOLDER'], current_user.profil_resmi)
                    if os.path.exists(eski_resim):
                        os.remove(eski_resim)
                
                filename = save_image(file)
                if filename:
                    current_user.profil_resmi = filename
        
        db.session.commit()
        flash('Profil başarıyla güncellendi!', 'success')
        return redirect(url_for('profil'))
    
    return render_template('profil_duzenle.html', kategoriler=kategoriler)

# Veritabanı başlatma ve örnek veriler
def veritabani_baslat():
    with app.app_context():
        db.create_all()
        
        # Admin kullanıcısı yoksa oluştur
        if Kullanici.query.filter_by(email='admin@acibadem.edu.tr').first() is None:
            admin = Kullanici(
                ad='Admin',
                soyad='User',
                email='admin@acibadem.edu.tr',
                rol='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        
        # Kategoriler yoksa ekle
        if Kategori.query.count() == 0:
            kategoriler = [
                Kategori(ad='Akademik'),
                Kategori(ad='Sosyal'),
                Kategori(ad='Spor'),
                Kategori(ad='Duyurular'),
                Kategori(ad='Etkinlikler')
            ]
            db.session.add_all(kategoriler)
            db.session.commit()
            
            # Örnek haberler
            ornek_haberler = [
                Haber(
                    baslik='2026 Bahar Dönemi Kayıt İşlemleri Başladı',
                    icerik='''Üniversitemizin 2026 Bahar dönemi kayıt işlemleri 15 Mart'ta başlayacaktır. 
                    Öğrencilerimizin belirlenen tarihlerde kayıt yaptırmaları gerekmektedir.
                    
                    Kayıt için gerekli belgeler:
                    - Öğrenci kimliği
                    - Harç dekontu
                    - Ders seçim formu
                    
                    Detaylı bilgi için öğrenci işleri ile iletişime geçebilirsiniz.''',
                    ozet='2026 Bahar dönemi kayıtları 15 Mart tarihinde başlıyor.',
                    yazar='Öğrenci İşleri',
                    gorsel_url='https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=800',
                    kategori_id=4
                ),
                Haber(
                    baslik='Üniversitemiz Basketbol Takımı Şampiyon Oldu',
                    icerik='''Üniversitemiz erkek basketbol takımı, dün gece oynanan final maçında
                    rakibini 78-65 yenerek şampiyonluğa ulaştı. Tüm takımımızı tebrik ediyoruz!
                    
                    Maçın en skoreri 24 sayı ile takım kaptanımız oldu. Antrenörümüz maç sonrası
                    yaptığı açıklamada takımın sezon boyunca gösterdiği özverili çalışmanın
                    meyvesini aldığını belirtti.''',
                    ozet='Erkek basketbol takımımız final maçını kazanarak şampiyon oldu.',
                    yazar='Spor Kulübü',
                    gorsel_url='https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800',
                    kategori_id=3
                ),
                Haber(
                    baslik='Yapay Zeka Konferansı 20 Mart\'ta Kampüste',
                    icerik='''Üniversitemiz Bilgisayar Mühendisliği bölümü tarafından düzenlenen
                    "Yapay Zeka ve Geleceği" konferansı 20 Mart tarihinde kampüsümüzde gerçekleşecek.
                    
                    Konferansta alanında uzman akademisyenler ve sektör temsilcileri konuşmacı
                    olarak yer alacak. Etkinlik tüm öğrencilere açıktır.
                    
                    Kayıt için: konferans.universite.edu.tr''',
                    ozet='Yapay Zeka konferansı 20 Mart\'ta kampüsümüzde düzenlenecek.',
                    yazar='Bilgisayar Mühendisliği',
                    gorsel_url='https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800',
                    kategori_id=1
                ),
                Haber(
                    baslik='Bahar Şenliği Hazırlıkları Devam Ediyor',
                    icerik='''Her yıl geleneksel olarak düzenlenen Bahar Şenliği için hazırlıklar
                    tüm hızıyla devam ediyor. Bu yıl şenlik 1-3 Mayıs tarihleri arasında
                    gerçekleştirilecek.
                    
                    Şenlik programında konserler, söyleşiler, spor etkinlikleri ve
                    yemek standları yer alacak. Öğrenci kulüpleri de çeşitli aktiviteler
                    düzenleyecek.''',
                    ozet='Bahar Şenliği 1-3 Mayıs tarihlerinde kampüste düzenlenecek.',
                    yazar='Öğrenci Konseyi',
                    gorsel_url='https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=800',
                    kategori_id=5
                )
            ]
            db.session.add_all(ornek_haberler)
            db.session.commit()

if __name__ == '__main__':
    veritabani_baslat()
    app.run(debug=True, port=5000)
