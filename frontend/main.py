import customtkinter as ctk
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import chardet
from pathlib import Path
import threading

class FileTranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Uygulama ayarları
        self.title("Makine Çeviri - Dosya Çeviricisi")
        self.geometry("1600x900")
        self.minsize(1400, 800)
        
        # Tema ayarları
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Ana değişkenler
        self.current_directory = None
        self.selected_file = None
        self.translated_files = {}
        self.supported_formats = ['.txt', '.json', '.xml', '.ini', '.cfg', '.properties', '.lang', '.yml', '.yaml']
        
        self.setup_ui()
        
    def setup_treeview_style(self):
        """TreeView stillerini başlangıçta ayarla"""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Başlangıçta dark mode (varsayılan)
        style.configure("Treeview", 
                       background="#2b2b2b",
                       foreground="white",
                       rowheight=25,
                       fieldbackground="#2b2b2b")
        style.configure("Treeview.Heading",
                       background="#1f538d",
                       foreground="white",
                       relief="flat")
        style.map("Treeview",
                 background=[('selected', '#1f538d')])
        
    def setup_ui(self):
        """Ana UI düzenlemesi"""
        # Ana grid yapılandırması - 4 eşit sütun
        self.grid_columnconfigure(0, weight=1)  # Sol panel - Orijinal dosya ağacı
        self.grid_columnconfigure(1, weight=1)  # Orta-sol panel - Orijinal önizleme
        self.grid_columnconfigure(2, weight=1)  # Orta-sağ panel - Çeviri önizleme
        self.grid_columnconfigure(3, weight=1)  # Sağ panel - Çeviri dosya ağacı
        self.grid_rowconfigure(0, weight=1)
        
        # Panelleri oluştur
        self.create_left_panel()           # Orijinal dosya ağacı
        self.create_middle_left_panel()    # Orijinal dosya önizleme
        self.create_middle_right_panel()   # Çeviri önizleme
        self.create_right_panel()          # Çeviri dosya ağacı
        
        # Alt panel - Kontroller
        self.create_bottom_panel()
        
    def create_left_panel(self):
        """Sol panel - Orijinal dosya ağacı"""
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)
        
        # Başlık
        title_label = ctk.CTkLabel(self.left_frame, text="Orijinal Dosyalar", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Klasör seçme butonu
        select_folder_btn = ctk.CTkButton(
            self.left_frame, 
            text="Klasör Seç",
            command=self.select_folder,
            height=32
        )
        select_folder_btn.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
        # Dosya ağacı
        tree_frame = ctk.CTkFrame(self.left_frame)
        tree_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview stili
        self.setup_treeview_style()
        
        self.file_tree = ttk.Treeview(tree_frame, show="tree headings", columns=("type",))
        self.file_tree.heading("#0", text="Dosya/Klasör")
        self.file_tree.heading("type", text="Tür")
        self.file_tree.column("type", width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self.file_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Dosya seçme eventi
        self.file_tree.bind("<<TreeviewSelect>>", self.on_file_select)
        
    def create_middle_left_panel(self):
        """Orta-sol panel - Orijinal dosya içeriği"""
        self.middle_left_frame = ctk.CTkFrame(self)
        self.middle_left_frame.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
        self.middle_left_frame.grid_rowconfigure(1, weight=1)
        self.middle_left_frame.grid_columnconfigure(0, weight=1)
        
        # Başlık
        self.middle_left_title = ctk.CTkLabel(self.middle_left_frame, text="Orijinal İçerik", 
                                             font=ctk.CTkFont(size=16, weight="bold"))
        self.middle_left_title.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # İçerik alanı
        self.original_content = ctk.CTkTextbox(self.middle_left_frame)
        self.original_content.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
    def create_middle_right_panel(self):
        """Orta-sağ panel - Çeviri önizleme"""
        self.middle_right_frame = ctk.CTkFrame(self)
        self.middle_right_frame.grid(row=0, column=2, padx=5, pady=10, sticky="nsew")
        self.middle_right_frame.grid_rowconfigure(1, weight=1)
        self.middle_right_frame.grid_columnconfigure(0, weight=1)
        
        # Başlık
        self.middle_right_title = ctk.CTkLabel(self.middle_right_frame, text="Çeviri Önizleme", 
                                              font=ctk.CTkFont(size=16, weight="bold"))
        self.middle_right_title.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # İçerik alanı
        self.translated_preview = ctk.CTkTextbox(self.middle_right_frame)
        self.translated_preview.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
    def create_right_panel(self):
        """Sağ panel - Çevrilmiş dosya ağacı"""
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=3, padx=(5, 10), pady=10, sticky="nsew")
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        # Başlık ve kontroller
        title_container = ctk.CTkFrame(self.right_frame)
        title_container.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        title_container.grid_columnconfigure(0, weight=1)
        
        self.right_title = ctk.CTkLabel(title_container, text="Çevrilmiş Dosyalar", 
                                       font=ctk.CTkFont(size=16, weight="bold"))
        self.right_title.grid(row=0, column=0, padx=0, pady=0, sticky="w")
        
        # Temizle butonu
        clear_btn = ctk.CTkButton(
            title_container,
            text="Temizle",
            command=self.clear_translated_files,
            height=28,
            width=80
        )
        clear_btn.grid(row=0, column=1, padx=10, pady=0, sticky="e")
        
        # Çevrilmiş dosya ağacı
        tree_container = ctk.CTkFrame(self.right_frame)
        tree_container.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Çevrilmiş dosyalar için Treeview
        self.translated_tree = ttk.Treeview(tree_container, show="tree headings", columns=("status",))
        self.translated_tree.heading("#0", text="Çevrilmiş Dosyalar")
        self.translated_tree.heading("status", text="Durum")
        self.translated_tree.column("status", width=80)
        
        # Scrollbar for translated tree
        trans_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.translated_tree.yview)
        self.translated_tree.configure(yscrollcommand=trans_scrollbar.set)
        
        self.translated_tree.grid(row=0, column=0, sticky="nsew")
        trans_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Çevrilmiş dosya seçme eventi
        self.translated_tree.bind("<<TreeviewSelect>>", self.on_translated_file_select)
        
    def create_bottom_panel(self):
        """Alt panel - Kontrol butonları"""
        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=(0, 10), sticky="ew")
        
        # Tema değiştirme
        theme_label = ctk.CTkLabel(self.bottom_frame, text="Tema:")
        theme_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.theme_switch = ctk.CTkSwitch(self.bottom_frame, text="Dark/Light", command=self.toggle_theme)
        self.theme_switch.grid(row=0, column=1, padx=10, pady=10)
        
        # Çeviri butonu
        self.translate_btn = ctk.CTkButton(
            self.bottom_frame,
            text="Çevir",
            command=self.handle_translation,
            state="disabled",
            height=40,
            width=120
        )
        self.translate_btn.grid(row=0, column=2, padx=20, pady=10)
        
        # Tümünü çevir checkbox
        self.translate_all_var = ctk.BooleanVar()
        self.translate_all_checkbox = ctk.CTkCheckBox(
            self.bottom_frame,
            text="Tüm desteklenen dosyaları çevir",
            variable=self.translate_all_var
        )
        self.translate_all_checkbox.grid(row=0, column=3, padx=20, pady=10)
        
        # Dışa aktarma butonu
        self.export_btn = ctk.CTkButton(
            self.bottom_frame,
            text="Dışa Aktar",
            command=self.export_files,
            state="disabled",
            height=40,
            width=120
        )
        self.export_btn.grid(row=0, column=4, padx=20, pady=10)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.bottom_frame)
        self.progress_bar.grid(row=0, column=5, padx=20, pady=10, sticky="ew")
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(self.bottom_frame, text="Dosya seçin...")
        self.status_label.grid(row=0, column=6, padx=10, pady=10)
        
    def select_folder(self):
        """Klasör seçme"""
        folder_path = filedialog.askdirectory(title="Çeviri için klasör seçin")
        if folder_path:
            self.current_directory = folder_path
            self.populate_file_tree(folder_path)
            self.status_label.configure(text=f"Klasör yüklendi: {os.path.basename(folder_path)}")
            
    def populate_file_tree(self, root_path):
        """Dosya ağacını doldurma"""
        # Ağacı temizle
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
            
        # Root item ekle
        root_item = self.file_tree.insert("", "end", text=f"📁 {os.path.basename(root_path)}", 
                                         values=("Klasör",), open=True)
        
        # Recursive olarak dosyaları ekle
        self._add_tree_items(root_item, root_path)
        
    def _add_tree_items(self, parent, path):
        """Ağaca öğeleri ekleme"""
        try:
            items = sorted(os.listdir(path))
            for item in items:
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    # Klasör
                    folder_item = self.file_tree.insert(parent, "end", text=f"📁 {item}", 
                                                       values=("Klasör",))
                    self._add_tree_items(folder_item, item_path)
                else:
                    # Dosya
                    ext = os.path.splitext(item)[1].lower()
                    
                    if ext in self.supported_formats:
                        file_type = "✅ Desteklenen"
                        icon = "📄"
                        print(f"Desteklenen dosya bulundu: {item} ({ext})")
                    else:
                        file_type = "❌ Desteklenmeyen"
                        icon = "📋"
                    
                    self.file_tree.insert(parent, "end", text=f"{icon} {item}", 
                                         values=(file_type,))
        except PermissionError:
            print("İzin hatası: Klasör okunamadı")
            pass
            
    def on_file_select(self, event):
        """Dosya seçildiğinde"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            file_path = self.get_file_path_from_tree(item)
            
            # Debug: Seçilen dosya yolunu yazdır
            print(f"Seçilen dosya yolu: {file_path}")
            
            if file_path and os.path.isfile(file_path):
                ext = os.path.splitext(file_path)[1].lower()
                print(f"Dosya uzantısı: {ext}")
                
                if ext in self.supported_formats:
                    self.selected_file = file_path
                    self.load_file_content(file_path)
                    self.translate_btn.configure(state="normal")
                    self.status_label.configure(text=f"Dosya seçildi: {os.path.basename(file_path)}")
                else:
                    self.status_label.configure(text="Desteklenmeyen dosya formatı!")
                    self.translate_btn.configure(state="disabled")
                    # İçeriği temizle
                    self.original_content.delete("1.0", "end")
                    self.middle_left_title.configure(text="Orijinal İçerik")
            else:
                if file_path:
                    # Klasör seçildi
                    self.status_label.configure(text="Klasör seçildi, dosya seçin")
                else:
                    self.status_label.configure(text="Geçersiz seçim")
                    
                self.translate_btn.configure(state="disabled")
                # İçeriği temizle
                self.original_content.delete("1.0", "end")
                self.middle_left_title.configure(text="Orijinal İçerik")
                
    def get_file_path_from_tree(self, item):
        """Tree item'dan dosya yolunu alma"""
        path_parts = []
        current_item = item
        
        while current_item:
            text = self.file_tree.item(current_item, "text")
            # İkon emojilerini temizle
            if text.startswith("📁 "):
                clean_text = text[2:]  # "📁 " kısmını çıkar
            elif text.startswith("📄 ") or text.startswith("📋 "):
                clean_text = text[2:]  # "📄 " veya "📋 " kısmını çıkar
            else:
                clean_text = text
            
            path_parts.insert(0, clean_text)
            current_item = self.file_tree.parent(current_item)
            
        if path_parts and self.current_directory:
            # İlk eleman root klasör adı, onu current_directory ile değiştir
            if len(path_parts) == 1:
                # Sadece root klasör seçildi
                return self.current_directory
            else:
                # Dosya veya alt klasör seçildi
                path_parts[0] = self.current_directory
                return os.path.join(*path_parts)
        return None
        
    def load_file_content(self, file_path):
        """Dosya içeriğini yükleme"""
        try:
            # Debug: Dosya yolunu kontrol et
            print(f"Dosya yükleniyor: {file_path}")
            
            # Dosyanın var olup olmadığını kontrol et
            if not os.path.exists(file_path):
                self.status_label.configure(text="Dosya bulunamadı!")
                return
                
            if not os.path.isfile(file_path):
                self.status_label.configure(text="Bu bir dosya değil!")
                return
            
            # Dosya kodlamasını algıla
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'
            
            # Dosyayı oku
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                
            # İçeriği temizle ve yeni içeriği ekle
            self.original_content.delete("1.0", "end")
            self.original_content.insert("1.0", content)
            
            # Başlığı güncelle
            self.middle_left_title.configure(text=f"Orijinal: {os.path.basename(file_path)}")
            
            # Debug: Başarılı yükleme
            print(f"Dosya başarıyla yüklendi. İçerik uzunluğu: {len(content)} karakter")
            
        except Exception as e:
            error_msg = f"Dosya okunamadı: {str(e)}\nDosya yolu: {file_path}"
            print(error_msg)
            messagebox.showerror("Hata", error_msg)
            self.status_label.configure(text="Dosya okuma hatası!")
            
    def translate_file(self):
        """Dosya çevirisi"""
        if not self.selected_file:
            return
            
        self.progress_bar.set(0.1)
        self.status_label.configure(text="Çeviri yapılıyor...")
        
        # İçeriği al
        content = self.original_content.get("1.0", "end-1c")
        
        # Çeviri işlemi (şimdilik demo, gerçek uygulamada API kullanılacak)
        self.progress_bar.set(0.5)
        translated = self._perform_translation(content)
        
        # Çeviri önizlemesini güncelle
        self.translated_preview.delete("1.0", "end")
        self.translated_preview.insert("1.0", translated)
        self.middle_right_title.configure(text=f"Çeviri: {os.path.basename(self.selected_file)}")
        
        # Çevrilmiş dosyayı kaydet
        self.translated_files[self.selected_file] = translated
        
        # Çevrilmiş dosyalar ağacını güncelle
        self.update_translated_files_tree()
        
        self.progress_bar.set(1.0)
        self.export_btn.configure(state="normal")
        self.status_label.configure(text="Çeviri tamamlandı!")
        
        # Yeni çevrilmiş dosyayı otomatik seç
        filename = os.path.basename(self.selected_file)
        for item in self.translated_tree.get_children():
            item_text = self.translated_tree.item(item, "text")
            if filename in item_text:
                self.translated_tree.selection_set(item)
                # Manuel olarak seçim eventini tetikle
                self.on_translated_file_select(None)
                break
        
        # Progress bar'ı sıfırla
        self.after(2000, lambda: self.progress_bar.set(0))
        
    def _perform_translation(self, content):
        """Çeviri işlemini gerçekleştir"""
        # Bu fonksiyon gerçek uygulamada çeviri API'si ile değiştirilecek
        # Örnek: Google Translate API, Azure Translator, vb.
        
        # Demo çeviri - sadece formatı koruyarak basit dönüşüm
        lines = content.split('\n')
        translated_lines = []
        
        for line in lines:
            if line.strip():
                # JSON, INI gibi formatları algıla ve uygun çeviri yap
                if '=' in line and not line.strip().startswith('#'):
                    # INI/Properties format
                    key, value = line.split('=', 1)
                    translated_value = f"[ÇEVRİLDİ] {value.strip()}"
                    translated_lines.append(f"{key}={translated_value}")
                elif line.strip().startswith('"') and ':' in line:
                    # JSON format
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key_part = parts[0].strip()
                        value_part = parts[1].strip().rstrip(',')
                        if value_part.startswith('"') and value_part.endswith('"'):
                            original_value = value_part[1:-1]
                            translated_value = f"[ÇEVRİLDİ] {original_value}"
                            comma = ',' if line.rstrip().endswith(',') else ''
                            translated_lines.append(f'{key_part}: "{translated_value}"{comma}')
                        else:
                            translated_lines.append(line)
                    else:
                        translated_lines.append(line)
                elif line.strip().startswith('#'):
                    # Yorum satırı
                    translated_lines.append(line)
                else:
                    # Düz metin
                    translated_lines.append(f"[ÇEVRİLDİ] {line}")
            else:
                translated_lines.append(line)
                
        return '\n'.join(translated_lines)
        
    def handle_translation(self):
        """Çeviri işlemini yönet - tek dosya veya toplu"""
        if self.translate_all_var.get():
            self.translate_all_supported_files()
        else:
            self.translate_file()
            
    def translate_all_supported_files(self):
        """Tüm desteklenen dosyaları çevir"""
        if not self.current_directory:
            messagebox.showwarning("Uyarı", "Önce bir klasör seçin!")
            return
            
        # Desteklenen dosyaları bul
        supported_files = []
        for root, dirs, files in os.walk(self.current_directory):
            for file in files:
                if os.path.splitext(file)[1].lower() in self.supported_formats:
                    supported_files.append(os.path.join(root, file))
        
        if not supported_files:
            messagebox.showinfo("Bilgi", "Desteklenen dosya bulunamadı!")
            return
            
        # Çeviri işlemini başlat
        self.status_label.configure(text=f"{len(supported_files)} dosya çevriliyor...")
        total_files = len(supported_files)
        
        for i, file_path in enumerate(supported_files):
            try:
                # Dosyayı oku
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    result = chardet.detect(raw_data)
                    encoding = result['encoding'] or 'utf-8'
                
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                
                # Çevir
                translated = self._perform_translation(content)
                self.translated_files[file_path] = translated
                
                # Progress güncelle
                progress = (i + 1) / total_files
                self.progress_bar.set(progress)
                self.status_label.configure(text=f"Çevriliyor: {i+1}/{total_files}")
                self.update()
                
            except Exception as e:
                print(f"Hata - {file_path}: {str(e)}")
                continue
        
        self.export_btn.configure(state="normal")
        self.status_label.configure(text=f"Toplam {len(self.translated_files)} dosya çevrildi!")
        
        # Çevrilmiş dosyalar ağacını güncelle
        self.update_translated_files_tree()
        
        # Progress bar'ı sıfırla
        self.after(3000, lambda: self.progress_bar.set(0))
        
    def on_translated_file_select(self, event):
        """Çevrilmiş dosya seçildiğinde"""
        selection = self.translated_tree.selection()
        if selection:
            item = selection[0]
            file_text = self.translated_tree.item(item, "text")
            
            # Icon'ları temizle
            clean_filename = file_text
            for icon in ["🔧 ", "📝 ", "⚙️ ", "📄 "]:
                if file_text.startswith(icon):
                    clean_filename = file_text[len(icon):]
                    break
                    
            # Orijinal dosya yolunu bul
            original_path = None
            for orig_path in self.translated_files.keys():
                if os.path.basename(orig_path) == clean_filename:
                    original_path = orig_path
                    break
            
            if original_path and original_path in self.translated_files:
                # Çevrilmiş içeriği orta-sağ panelde göster
                translated_content = self.translated_files[original_path]
                self.translated_preview.delete("1.0", "end")
                self.translated_preview.insert("1.0", translated_content)
                self.middle_right_title.configure(text=f"Çeviri: {clean_filename}")
                
                print(f"Çevrilmiş dosya seçildi: {clean_filename}")
                print(f"İçerik uzunluğu: {len(translated_content)} karakter")
            else:
                self.translated_preview.delete("1.0", "end")
                self.middle_right_title.configure(text="Çeviri Önizleme")
                print(f"Çevrilmiş dosya bulunamadı: {clean_filename}")
                
    def update_translated_files_tree(self):
        """Çevrilmiş dosyalar ağacını güncelle"""
        print(f"Çevrilmiş dosyalar ağacı güncelleniyor. Toplam dosya: {len(self.translated_files)}")
        
        # Ağacı temizle
        for item in self.translated_tree.get_children():
            self.translated_tree.delete(item)
        
        # Çevrilmiş dosyaları ekle
        for file_path in self.translated_files.keys():
            filename = os.path.basename(file_path)
            ext = os.path.splitext(filename)[1].lower()
            
            # İkon seç
            if ext in ['.json']:
                icon = "🔧"
            elif ext in ['.txt', '.lang']:
                icon = "📝"
            elif ext in ['.ini', '.cfg']:
                icon = "⚙️"
            else:
                icon = "📄"
                
            tree_item = self.translated_tree.insert("", "end", text=f"{icon} {filename}", 
                                       values=("✅ Çevrildi",))
            print(f"Çevrilmiş dosya eklendi: {icon} {filename}")
                                       
    def clear_translated_files(self):
        """Çevrilmiş dosyaları temizle"""
        if self.translated_files:
            result = messagebox.askyesno("Onay", "Tüm çevrilmiş dosyaları temizlemek istediğinizden emin misiniz?")
            if result:
                self.translated_files.clear()
                self.update_translated_files_tree()
                self.translated_preview.delete("1.0", "end")
                self.middle_right_title.configure(text="Çeviri Önizleme")
                self.export_btn.configure(state="disabled")
                self.status_label.configure(text="Çevrilmiş dosyalar temizlendi")
        else:
            messagebox.showinfo("Bilgi", "Temizlenecek çevrilmiş dosya yok!")
        
    def export_files(self):
        """Çevrilmiş dosyaları dışa aktarma"""
        if not self.translated_files:
            messagebox.showwarning("Uyarı", "Dışa aktarılacak çevrilmiş dosya yok!")
            return
            
        export_dir = filedialog.askdirectory(title="Çevrilmiş dosyaları kaydetmek için klasör seçin")
        if export_dir:
            try:
                exported_count = 0
                
                # Çevrilmiş dosyalar için alt klasör oluştur
                translated_dir = os.path.join(export_dir, "translated_files")
                os.makedirs(translated_dir, exist_ok=True)
                
                for original_path, translated_content in self.translated_files.items():
                    # Orijinal klasör yapısını koru
                    if self.current_directory and original_path.startswith(self.current_directory):
                        # Relative path al
                        rel_path = os.path.relpath(original_path, self.current_directory)
                        rel_dir = os.path.dirname(rel_path)
                        
                        # Hedef klasörü oluştur
                        target_dir = os.path.join(translated_dir, rel_dir) if rel_dir else translated_dir
                        os.makedirs(target_dir, exist_ok=True)
                        
                        # Dosya adını hazırla
                        filename = os.path.basename(original_path)
                        name, ext = os.path.splitext(filename)
                        new_filename = f"{name}_translated{ext}"
                        
                        # Dosyayı kaydet
                        export_path = os.path.join(target_dir, new_filename)
                    else:
                        # Basit dosya adı
                        filename = os.path.basename(original_path)
                        name, ext = os.path.splitext(filename)
                        new_filename = f"{name}_translated{ext}"
                        export_path = os.path.join(translated_dir, new_filename)
                    
                    with open(export_path, 'w', encoding='utf-8') as f:
                        f.write(translated_content)
                    exported_count += 1
                    
                messagebox.showinfo("Başarılı", 
                    f"{exported_count} dosya başarıyla dışa aktarıldı!\n"
                    f"Konum: {translated_dir}")
                self.status_label.configure(text=f"{exported_count} dosya dışa aktarıldı")
                
            except Exception as e:
                messagebox.showerror("Hata", f"Dışa aktarma hatası: {str(e)}")
                
    def toggle_theme(self):
        """Tema değiştirme"""
        if self.theme_switch.get():
            ctk.set_appearance_mode("light")
            self.update_treeview_style("light")
        else:
            ctk.set_appearance_mode("dark")
            self.update_treeview_style("dark")
            
    def update_treeview_style(self, mode):
        """TreeView stillerini tema değişikliğine göre güncelle"""
        style = ttk.Style()
        
        if mode == "light":
            # Light mode renkleri
            style.configure("Treeview",
                           background="white",
                           foreground="black",
                           rowheight=25,
                           fieldbackground="white")
            style.configure("Treeview.Heading",
                           background="#e0e0e0",
                           foreground="black",
                           relief="flat")
            style.map("Treeview",
                     background=[('selected', '#0078d4')])
        else:
            # Dark mode renkleri
            style.configure("Treeview",
                           background="#2b2b2b",
                           foreground="white",
                           rowheight=25,
                           fieldbackground="#2b2b2b")
            style.configure("Treeview.Heading",
                           background="#1f538d",
                           foreground="white",
                           relief="flat")
            style.map("Treeview",
                     background=[('selected', '#1f538d')])
        
        # TreeView'ları yeniden çiz
        if hasattr(self, 'file_tree'):
            self.file_tree.update()
        if hasattr(self, 'translated_tree'):
            self.translated_tree.update()

if __name__ == "__main__":
    app = FileTranslatorApp()
    app.mainloop()
