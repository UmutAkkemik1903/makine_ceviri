import customtkinter as ctk
import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import chardet
from pathlib import Path
import threading
import webbrowser

from deepl_client import build_client_from_env

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

        # Dil seçenekleri (hedef ve kaynak)
        self.target_languages = {
            "Türkçe (TR)": "TR",
            "İngilizce (EN)": "EN",
            "Almanca (DE)": "DE",
            "Fransızca (FR)": "FR",
            "İspanyolca (ES)": "ES",
            "İtalyanca (IT)": "IT",
            "Portekizce (PT)": "PT",
            "Felemenkçe (NL)": "NL",
            "Rusça (RU)": "RU",
            "Arapça (AR)": "AR",
            "Japonca (JA)": "JA",
            "Korece (KO)": "KO",
            "Çince (ZH)": "ZH",
            "İsveççe (SV)": "SV",
            "Lehçe (PL)": "PL",
        }
        self.source_languages = {"Otomatik (Algıla)": None}
        self.source_languages.update(self.target_languages)

        self.target_lang_var = tk.StringVar(value="Türkçe (TR)")
        self.source_lang_var = tk.StringVar(value="Otomatik (Algıla)")
        self.translation_client = None

        # UI durum değişkenleri
        self.search_var = tk.StringVar()
        self.search_result_var = tk.StringVar(value="Filtre: tüm dosyalar")
        self.folder_badge_text = tk.StringVar(value="Klasör: -")
        self.translation_badge_text = tk.StringVar(value="Çevrilen dosya: 0")
        self.original_stats_text = tk.StringVar(value="Satır: 0    Karakter: 0")
        self.translated_stats_text = tk.StringVar(value="Satır: 0    Karakter: 0")
        
        self.setup_ui()
        self.initialize_translation_client()
        
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
        self.grid_rowconfigure(0, weight=0)     # Üst başlık
        self.grid_rowconfigure(1, weight=1)     # Ana içerik
        self.grid_rowconfigure(2, weight=0)     # Alt kontroller

        # Üst bilgi paneli
        self.create_header()

        # Panelleri oluştur
        self.create_left_panel()           # Orijinal dosya ağacı
        self.create_middle_left_panel()    # Orijinal dosya önizleme
        self.create_middle_right_panel()   # Çeviri önizleme
        self.create_right_panel()          # Çeviri dosya ağacı

        # Alt panel - Kontroller
        self.create_bottom_panel()

    def create_header(self):
        """Üst bilgi paneli"""
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_columnconfigure(2, weight=0)

        # Başlık ve alt başlık
        title_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_container.grid(row=0, column=0, sticky="w")

        app_title = ctk.CTkLabel(
            title_container,
            text="Makine Çeviri Paneli",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        app_title.grid(row=0, column=0, sticky="w")

        app_subtitle = ctk.CTkLabel(
            title_container,
            text="Dosyalarınızı tek tıkla keşfedin, önizleyin ve çevirin",
            font=ctk.CTkFont(size=13),
            text_color=("#475569", "#cbd5ff")
        )
        app_subtitle.grid(row=1, column=0, pady=(4, 0), sticky="w")

        # Durum kartları
        stats_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        stats_container.grid(row=0, column=1, padx=10, sticky="ew")
        stats_container.grid_columnconfigure((0, 1), weight=1)

        folder_card = ctk.CTkFrame(stats_container, corner_radius=12, fg_color=("#f8fafc", "#1f2933"))
        folder_card.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        folder_card.grid_columnconfigure(1, weight=1)
        folder_icon = ctk.CTkLabel(folder_card, text="📁", font=ctk.CTkFont(size=18))
        folder_icon.grid(row=0, column=0, padx=(12, 6), pady=10)
        folder_value = ctk.CTkLabel(
            folder_card,
            textvariable=self.folder_badge_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            wraplength=220,
            justify="left",
            text_color=("#0f172a", "#e2e8f0")
        )
        folder_value.grid(row=0, column=1, padx=(0, 12), sticky="w")

        translation_card = ctk.CTkFrame(stats_container, corner_radius=12, fg_color=("#f8fafc", "#1f2933"))
        translation_card.grid(row=0, column=1, padx=(6, 0), sticky="ew")
        translation_card.grid_columnconfigure(1, weight=1)
        translation_icon = ctk.CTkLabel(translation_card, text="⚡", font=ctk.CTkFont(size=18))
        translation_icon.grid(row=0, column=0, padx=(12, 6), pady=10)
        translation_value = ctk.CTkLabel(
            translation_card,
            textvariable=self.translation_badge_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            wraplength=220,
            justify="left",
            text_color=("#0f172a", "#e2e8f0")
        )
        translation_value.grid(row=0, column=1, padx=(0, 12), sticky="w")

        # Hızlı aksiyonlar
        actions_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        actions_container.grid(row=0, column=2, sticky="e")

        guide_btn = ctk.CTkButton(
            actions_container,
            text="Kılavuzu Aç",
            command=self.open_usage_guide,
            width=120
        )
        guide_btn.grid(row=0, column=0, padx=(0, 6))

        log_btn = ctk.CTkButton(
            actions_container,
            text="Çeviri Günlüğü",
            command=self.open_translation_log,
            width=140
        )
        log_btn.grid(row=0, column=1)

        self.update_header_stats()

    def _open_path_with_default_app(self, path: Path, title: str):
        """Belirtilen dosyayı varsayılan uygulama ile aç"""
        try:
            if os.name == "nt":
                os.startfile(path)
            else:
                webbrowser.open(path.as_uri())
        except Exception as exc:
            messagebox.showerror(title, f"Açılamadı: {exc}")

    def update_header_stats(self):
        """Üst panel ve rozetleri güncelle"""
        if self.current_directory:
            folder_name = os.path.basename(self.current_directory.rstrip(os.sep)) or self.current_directory
            self.folder_badge_text.set(f"Klasör: {folder_name}\n{self.current_directory}")
        else:
            self.folder_badge_text.set("Klasör: -")

        translated_count = len(self.translated_files)
        self.translation_badge_text.set(f"Çevrilen dosya: {translated_count}")

    def open_usage_guide(self):
        """Kullanım kılavuzunu kullanıcıya aç"""
        guide_path = Path(__file__).resolve().parent / "KULLANIM.md"
        if guide_path.exists():
            self._open_path_with_default_app(guide_path, "Kılavuz")
        else:
            messagebox.showwarning("Kılavuz bulunamadı", "KULLANIM.md dosyası mevcut değil.")

    def open_translation_log(self):
        """Çeviri log dosyasını aç"""
        log_path = Path(__file__).resolve().parent.parent / "images" / "translation_log.txt"
        if log_path.exists():
            self._open_path_with_default_app(log_path, "Çeviri Günlüğü")
        else:
            messagebox.showwarning("Günlük bulunamadı", "translation_log.txt dosyası mevcut değil.")

    def refresh_current_folder(self):
        """Mevcut klasörü yeniden yükle"""
        if self.current_directory and os.path.isdir(self.current_directory):
            self.populate_file_tree(self.current_directory)
            self.apply_tree_search(self.search_var.get())
            self.update_header_stats()
            self.status_label.configure(text=f"Klasör yenilendi: {os.path.basename(self.current_directory)}")
        else:
            messagebox.showinfo("Klasör", "Önce bir klasör seçmelisiniz.")

    def clear_search_query(self):
        """Dosya ağacı aramasını temizle"""
        if self.search_var.get():
            self.search_var.set("")
            self.apply_tree_search("")

    def apply_tree_search(self, query):
        """Dosya ağacında arama uygula"""
        if not hasattr(self, "file_tree"):
            return

        normalized = query.strip().lower()
        matched_items = []

        for item in self._iter_tree_items(self.file_tree):
            text = self.file_tree.item(item, "text").lower()
            tags = list(self.file_tree.item(item, "tags"))

            if normalized and normalized in text:
                if "match" not in tags:
                    tags.append("match")
                matched_items.append(item)
                parent = self.file_tree.parent(item)
                while parent:
                    self.file_tree.item(parent, open=True)
                    parent = self.file_tree.parent(parent)
            else:
                if "match" in tags:
                    tags.remove("match")

            self.file_tree.item(item, tags=tuple(tags))

        if normalized:
            if matched_items:
                first = matched_items[0]
                self.file_tree.selection_set(first)
                self.file_tree.focus(first)
                self.file_tree.see(first)
                self.search_result_var.set(f"{len(matched_items)} sonuç bulundu")
            else:
                self.file_tree.selection_remove(self.file_tree.selection())
                self.search_result_var.set("Sonuç bulunamadı")
        else:
            self.search_result_var.set("Filtre: tüm dosyalar")

    def _iter_tree_items(self, tree, parent=""):
        """Treeview elemanları üzerinde dolaş"""
        for item in tree.get_children(parent):
            yield item
            yield from self._iter_tree_items(tree, item)

    def update_original_stats(self, content, encoding=None):
        """Orijinal içerik istatistiklerini güncelle"""
        content = content or ""
        line_count = content.count("\n")
        if content and not content.endswith("\n"):
            line_count += 1
        char_count = len(content)

        if encoding:
            encoding_display = encoding.upper() if isinstance(encoding, str) else str(encoding)
            info = f"Satır: {line_count}    Karakter: {char_count}    Kodlama: {encoding_display}"
        else:
            info = f"Satır: {line_count}    Karakter: {char_count}"
        self.original_stats_text.set(info)

    def update_translated_stats(self, content):
        """Çeviri önizleme istatistiklerini güncelle"""
        content = content or ""
        line_count = content.count("\n")
        if content and not content.endswith("\n"):
            line_count += 1
        char_count = len(content)
        info = f"Satır: {line_count}    Karakter: {char_count}"
        self.translated_stats_text.set(info)

    def copy_original_to_clipboard(self):
        """Orijinal içeriği panoya kopyala"""
        content = self.original_content.get("1.0", "end-1c")
        if content.strip():
            self.clipboard_clear()
            self.clipboard_append(content)
            self.status_label.configure(text="Orijinal içerik panoya kopyalandı")
        else:
            self.status_label.configure(text="Kopyalanacak içerik bulunamadı")

    def copy_translated_to_clipboard(self):
        """Çevrilmiş içeriği panoya kopyala"""
        content = self.translated_preview.get("1.0", "end-1c")
        if content.strip():
            self.clipboard_clear()
            self.clipboard_append(content)
            self.status_label.configure(text="Çevrilmiş içerik panoya kopyalandı")
        else:
            self.status_label.configure(text="Kopyalanmış çeviri yok")

    def initialize_translation_client(self):
        """DeepL istemcisini ortam değişkenlerinden başlat"""
        try:
            self.translation_client = build_client_from_env()
        except Exception as e:
            self.translation_client = None
            messagebox.showwarning(
                "DeepL Ayarı",
                "DeepL API anahtarı bulunamadı veya okunamadı."
                f"\nÇeviri işlemi yapılamayacak.\n\nDetay: {str(e)}",
            )
            if hasattr(self, "status_label"):
                self.status_label.configure(text="DeepL anahtarı eksik!")
        
    def create_left_panel(self):
        """Sol panel - Orijinal dosya ağacı"""
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="nsew")
        self.left_frame.grid_rowconfigure(3, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)
        
        # Başlık ve klasör seçimi
        header_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header_frame,
            text="Orijinal Dosyalar",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="w")
        
        select_folder_btn = ctk.CTkButton(
            header_frame,
            text="Klasör Seç",
            command=self.select_folder,
            height=32
        )
        select_folder_btn.grid(row=0, column=1, padx=0, pady=0, sticky="e")

        # Seçili klasör bilgisi
        self.folder_path_label = ctk.CTkLabel(
            self.left_frame,
            textvariable=self.folder_badge_text,
            anchor="w",
            wraplength=260,
            font=ctk.CTkFont(size=12),
            text_color=("#334155", "#d0e2ff")
        )
        self.folder_path_label.grid(row=1, column=0, columnspan=2, padx=10, pady=(6, 0), sticky="ew")

        # Arama ve filtre alanı
        search_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        search_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=(10, 6), sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Dosya veya klasör ara..."
        )
        self.search_entry.grid(row=0, column=0, padx=(0, 8), pady=0, sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda event: self.apply_tree_search(self.search_var.get()))

        clear_search_btn = ctk.CTkButton(
            search_frame,
            text="Temizle",
            width=70,
            height=30,
            command=self.clear_search_query
        )
        clear_search_btn.grid(row=0, column=1, padx=(0, 8), pady=0)

        refresh_btn = ctk.CTkButton(
            search_frame,
            text="Yenile",
            width=70,
            height=30,
            command=self.refresh_current_folder
        )
        refresh_btn.grid(row=0, column=2, padx=0, pady=0)

        search_result_label = ctk.CTkLabel(
            search_frame,
            textvariable=self.search_result_var,
            anchor="w",
            text_color=("#175cd3", "#8cb7ff"),
            font=ctk.CTkFont(size=11)
        )
        search_result_label.grid(row=1, column=0, columnspan=3, pady=(6, 0), sticky="w")
        
        # Dosya ağacı
        tree_frame = ctk.CTkFrame(self.left_frame)
        tree_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="nsew")
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
        self.update_match_tag_style()
        
        # Dosya seçme eventi
        self.file_tree.bind("<<TreeviewSelect>>", self.on_file_select)
        
    def create_middle_left_panel(self):
        """Orta-sol panel - Orijinal dosya içeriği"""
        self.middle_left_frame = ctk.CTkFrame(self)
        self.middle_left_frame.grid(row=1, column=1, padx=5, pady=10, sticky="nsew")
        self.middle_left_frame.grid_rowconfigure(1, weight=1)
        self.middle_left_frame.grid_columnconfigure(0, weight=1)
        
        # Başlık satırı
        header_frame = ctk.CTkFrame(self.middle_left_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        self.middle_left_title = ctk.CTkLabel(
            header_frame,
            text="Orijinal İçerik",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.middle_left_title.grid(row=0, column=0, sticky="w")

        copy_original_btn = ctk.CTkButton(
            header_frame,
            text="Panoya Kopyala",
            height=30,
            command=self.copy_original_to_clipboard
        )
        copy_original_btn.grid(row=0, column=1, padx=(10, 0), sticky="e")
        
        # İçerik alanı
        self.original_content = ctk.CTkTextbox(self.middle_left_frame)
        self.original_content.configure(wrap="word")
        self.original_content.grid(row=1, column=0, padx=10, pady=(6, 10), sticky="nsew")
        self.original_content.bind("<KeyRelease>", lambda event: self.update_original_stats(self.original_content.get("1.0", "end-1c")))

        stats_frame = ctk.CTkFrame(self.middle_left_frame, fg_color="transparent")
        stats_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.original_stats_label = ctk.CTkLabel(
            stats_frame,
            textvariable=self.original_stats_text,
            anchor="w",
            font=ctk.CTkFont(size=11)
        )
        self.original_stats_label.grid(row=0, column=0, sticky="w")
        
    def create_middle_right_panel(self):
        """Orta-sağ panel - Çeviri önizleme"""
        self.middle_right_frame = ctk.CTkFrame(self)
        self.middle_right_frame.grid(row=1, column=2, padx=5, pady=10, sticky="nsew")
        self.middle_right_frame.grid_rowconfigure(1, weight=1)
        self.middle_right_frame.grid_columnconfigure(0, weight=1)
        
        header_frame = ctk.CTkFrame(self.middle_right_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        self.middle_right_title = ctk.CTkLabel(
            header_frame,
            text="Çeviri Önizleme",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.middle_right_title.grid(row=0, column=0, sticky="w")

        copy_translated_btn = ctk.CTkButton(
            header_frame,
            text="Panoya Kopyala",
            height=30,
            command=self.copy_translated_to_clipboard
        )
        copy_translated_btn.grid(row=0, column=1, padx=(10, 0), sticky="e")
        
        # İçerik alanı
        self.translated_preview = ctk.CTkTextbox(self.middle_right_frame, state="normal")
        self.translated_preview.configure(wrap="word")
        self.translated_preview.grid(row=1, column=0, padx=10, pady=(6, 10), sticky="nsew")
        self.translated_preview.bind("<KeyRelease>", lambda event: self.update_translated_stats(self.translated_preview.get("1.0", "end-1c")))

        stats_frame = ctk.CTkFrame(self.middle_right_frame, fg_color="transparent")
        stats_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.translated_stats_label = ctk.CTkLabel(
            stats_frame,
            textvariable=self.translated_stats_text,
            anchor="w",
            font=ctk.CTkFont(size=11)
        )
        self.translated_stats_label.grid(row=0, column=0, sticky="w")
        
    def create_right_panel(self):
        """Sağ panel - Çevrilmiş dosya ağacı"""
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=1, column=3, padx=(5, 10), pady=10, sticky="nsew")
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        # Başlık ve kontroller
        title_container = ctk.CTkFrame(self.right_frame)
        title_container.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        title_container.grid_columnconfigure(0, weight=1)
        
        self.right_title = ctk.CTkLabel(title_container, text="Çevrilmiş Dosyalar", 
                                       font=ctk.CTkFont(size=16, weight="bold"))
        self.right_title.grid(row=0, column=0, padx=0, pady=0, sticky="w")
        
        badge_label = ctk.CTkLabel(
            title_container,
            textvariable=self.translation_badge_text,
            font=ctk.CTkFont(size=12),
            text_color=("#1d4ed8", "#8cb7ff")
        )
        badge_label.grid(row=1, column=0, sticky="w", pady=(6, 0))

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
        self.bottom_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=(0, 10), sticky="ew")
        self.bottom_frame.grid_columnconfigure(9, weight=1)
        
        # Tema değiştirme
        theme_label = ctk.CTkLabel(self.bottom_frame, text="Tema:")
        theme_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.theme_switch = ctk.CTkSwitch(self.bottom_frame, text="Dark/Light", command=self.toggle_theme)
        self.theme_switch.grid(row=0, column=1, padx=10, pady=10)

        # Kaynak dil seçimi
        source_label = ctk.CTkLabel(self.bottom_frame, text="Kaynak Dil:")
        source_label.grid(row=0, column=2, padx=(10, 5), pady=10)

        self.source_lang_menu = ctk.CTkOptionMenu(
            self.bottom_frame,
            variable=self.source_lang_var,
            values=list(self.source_languages.keys())
        )
        self.source_lang_menu.grid(row=0, column=3, padx=(0, 15), pady=10)

        # Hedef dil seçimi
        target_label = ctk.CTkLabel(self.bottom_frame, text="Hedef Dil:")
        target_label.grid(row=0, column=4, padx=(5, 5), pady=10)

        self.target_lang_menu = ctk.CTkOptionMenu(
            self.bottom_frame,
            variable=self.target_lang_var,
            values=list(self.target_languages.keys())
        )
        self.target_lang_menu.grid(row=0, column=5, padx=(0, 20), pady=10)
        
        # Çeviri butonu
        self.translate_btn = ctk.CTkButton(
            self.bottom_frame,
            text="Çevir",
            command=self.handle_translation,
            state="disabled",
            height=40,
            width=120
        )
        self.translate_btn.grid(row=0, column=6, padx=20, pady=10)
        
        # Tümünü çevir checkbox
        self.translate_all_var = ctk.BooleanVar()
        self.translate_all_checkbox = ctk.CTkCheckBox(
            self.bottom_frame,
            text="Tüm desteklenen dosyaları çevir",
            variable=self.translate_all_var
        )
        self.translate_all_checkbox.grid(row=0, column=7, padx=20, pady=10)
        
        # Dışa aktarma butonu
        self.export_btn = ctk.CTkButton(
            self.bottom_frame,
            text="Dışa Aktar",
            command=self.export_files,
            state="disabled",
            height=40,
            width=120
        )
        self.export_btn.grid(row=0, column=8, padx=20, pady=10)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.bottom_frame)
        self.progress_bar.grid(row=0, column=9, padx=20, pady=10, sticky="ew")
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(self.bottom_frame, text="Dosya seçin...")
        self.status_label.grid(row=0, column=10, padx=10, pady=10)
        
    def select_folder(self):
        """Klasör seçme"""
        folder_path = filedialog.askdirectory(title="Çeviri için klasör seçin")
        if folder_path:
            self.current_directory = folder_path
            self.populate_file_tree(folder_path)
            self.clear_search_query()
            self.update_header_stats()
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
        self.search_result_var.set("Filtre: tüm dosyalar")
        
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
                    self.update_original_stats("")
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
                self.update_original_stats("")
                
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
            self.update_original_stats(content, encoding)
            
            # Debug: Başarılı yükleme
            print(f"Dosya başarıyla yüklendi. İçerik uzunluğu: {len(content)} karakter")
            
        except Exception as e:
            error_msg = f"Dosya okunamadı: {str(e)}\nDosya yolu: {file_path}"
            print(error_msg)
            messagebox.showerror("Hata", error_msg)
            self.status_label.configure(text="Dosya okuma hatası!")
            self.update_original_stats("")
            
    def translate_file(self):
        """Dosya çevirisi"""
        if not self.selected_file:
            return
            
        self.progress_bar.set(0.1)
        self.status_label.configure(text="Çeviri yapılıyor...")
        
        # İçeriği al
        content = self.original_content.get("1.0", "end-1c")
        
        # Çeviri işlemi
        self.progress_bar.set(0.5)
        try:
            translated = self._perform_translation(content, self.selected_file)
        except Exception as e:
            self.progress_bar.set(0)
            self.status_label.configure(text="Çeviri başarısız!")
            messagebox.showerror("Çeviri Hatası", str(e))
            return
        
        # Çeviri önizlemesini güncelle
        self.translated_preview.delete("1.0", "end")
        self.translated_preview.insert("1.0", translated)
        self.middle_right_title.configure(text=f"Çeviri: {os.path.basename(self.selected_file)}")
        self.update_translated_stats(translated)
        
        # Çevrilmiş dosyayı kaydet
        self.translated_files[self.selected_file] = translated
        
        # Çevrilmiş dosyalar ağacını güncelle
        self.update_translated_files_tree()
        self.update_header_stats()
        
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
        
    def _perform_translation(self, content, file_path=None):
        """Seçili dilleri kullanarak DeepL üzerinden çeviri yap"""
        if not self.translation_client:
            raise RuntimeError("DeepL API istemcisi hazır değil.")

        source_code, target_code = self._get_selected_language_codes()
        ext = os.path.splitext(file_path)[1].lower() if file_path else ""

        try:
            if ext in ['.ini', '.cfg', '.properties', '.lang']:
                return self._translate_key_value_content(content, source_code, target_code)
            if ext == '.json':
                return self._translate_json_content(content, source_code, target_code)

            return self._translate_plain_content(content, source_code, target_code)
        except Exception as e:
            raise RuntimeError(f"DeepL çeviri hatası: {e}") from e

    def _translate_plain_content(self, content, source_code, target_code):
        sanitized_text, placeholders = self._mask_tags(content)
        translated = self.translation_client.translate_text(
            sanitized_text,
            target_lang=target_code,
            source_lang=source_code,
            preserve_formatting=True,
        )
        if isinstance(translated, list):
            translated = translated[0] if translated else ""
        return self._restore_placeholders(translated, placeholders)

    def _get_selected_language_codes(self):
        source_label = self.source_lang_var.get()
        target_label = self.target_lang_var.get()
        target_code = self.target_languages.get(target_label, 'TR')
        source_code = self.source_languages.get(source_label)
        return source_code or None, target_code

    def _prepare_segments_for_translation(self, segments):
        sanitized_segments = []
        placeholder_maps = []
        for segment in segments:
            sanitized, mapping = self._mask_tags(segment)
            sanitized_segments.append(sanitized)
            placeholder_maps.append(mapping)
        return sanitized_segments, placeholder_maps

    def _mask_tags(self, text):
        if not text:
            return text, {}

        tag_pattern = re.compile(r'<[^>\n\r]+>')
        placeholders = {}
        parts = []
        last_idx = 0

        for idx, match in enumerate(tag_pattern.finditer(text)):
            parts.append(text[last_idx:match.start()])
            placeholder = f"__DEEPL_TAG_{idx}__"
            parts.append(placeholder)
            placeholders[placeholder] = match.group(0)
            last_idx = match.end()

        parts.append(text[last_idx:])
        sanitized_text = ''.join(parts)
        return sanitized_text, placeholders

    def _restore_placeholders(self, text, placeholders):
        if not placeholders or not text:
            return text
        for placeholder, original in placeholders.items():
            text = text.replace(placeholder, original)
        return text

    def _translate_key_value_content(self, content, source_code, target_code):
        lines = content.splitlines()
        trailing_newline = content.endswith('\n')
        segments = []
        instructions = []

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#') or stripped.startswith(';'):
                instructions.append(('raw', line))
                continue

            if '=' in line:
                key_part, value_part = line.split('=', 1)
                segments.append(value_part.strip())
                instructions.append(('kv', key_part.rstrip(), len(segments) - 1))
            else:
                segments.append(stripped)
                leading_ws = line[:len(line) - len(line.lstrip())]
                instructions.append(('plain', len(segments) - 1, leading_ws))

        if not segments:
            return content

        sanitized_segments, placeholder_maps = self._prepare_segments_for_translation(segments)

        translated_segments = self.translation_client.translate_text(
            sanitized_segments,
            target_lang=target_code,
            source_lang=source_code,
            preserve_formatting=True,
        )
        if isinstance(translated_segments, str):
            translated_segments = [translated_segments]
        translated_segments = [
            self._restore_placeholders(translated_segments[idx], placeholder_maps[idx])
            for idx in range(len(translated_segments))
        ]

        new_lines = []
        for instruction in instructions:
            if instruction[0] == 'raw':
                new_lines.append(instruction[1])
            elif instruction[0] == 'kv':
                _, key_part, idx = instruction
                new_lines.append(f"{key_part} = {translated_segments[idx]}")
            else:
                _, idx, leading_ws = instruction
                new_lines.append(f"{leading_ws}{translated_segments[idx]}")

        result = '\n'.join(new_lines)
        if trailing_newline and not result.endswith('\n'):
            result += '\n'
        return result

    def _translate_json_content(self, content, source_code, target_code):
        trailing_newline = content.endswith('\n')
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return self.translation_client.translate_text(
                content,
                target_lang=target_code,
                source_lang=source_code,
                preserve_formatting=True,
            )

        references = []
        self._collect_json_string_nodes(data, references)

        if references:
            original_values = [value for (_, _, value) in references]
            sanitized_values, placeholder_maps = self._prepare_segments_for_translation(original_values)
            translated_values = self.translation_client.translate_text(
                sanitized_values,
                target_lang=target_code,
                source_lang=source_code,
                preserve_formatting=True,
            )
            if isinstance(translated_values, str):
                translated_values = [translated_values]
            restored_values = [
                self._restore_placeholders(translated_values[idx], placeholder_maps[idx])
                for idx in range(len(translated_values))
            ]
            for (container, key, _), translated in zip(references, restored_values):
                container[key] = translated

        result = json.dumps(data, ensure_ascii=False, indent=4)
        if trailing_newline and not result.endswith('\n'):
            result += '\n'
        return result

    def _collect_json_string_nodes(self, obj, references):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str):
                    references.append((obj, key, value))
                elif isinstance(value, (dict, list)):
                    self._collect_json_string_nodes(value, references)
        elif isinstance(obj, list):
            for index, item in enumerate(obj):
                if isinstance(item, str):
                    references.append((obj, index, item))
                elif isinstance(item, (dict, list)):
                    self._collect_json_string_nodes(item, references)
        
    def handle_translation(self):
        """Çeviri işlemini yönet - tek dosya veya toplu"""
        if not self.translation_client:
            messagebox.showerror(
                "DeepL Ayarı",
                "DeepL API anahtarı bulunamadı. Lütfen .env dosyanızı kontrol edin.",
            )
            return

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
        
        errors = []
        last_success_path = None
        last_translated_content = ""
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
                translated = self._perform_translation(content, file_path)
                self.translated_files[file_path] = translated
                last_success_path = file_path
                last_translated_content = translated
                
                # Progress güncelle
                progress = (i + 1) / total_files
                self.progress_bar.set(progress)
                self.status_label.configure(text=f"Çevriliyor: {i+1}/{total_files}")
                self.update()
                
            except Exception as e:
                print(f"Hata - {file_path}: {str(e)}")
                errors.append((file_path, str(e)))
                continue
        
        self.export_btn.configure(state="normal")
        self.status_label.configure(text=f"Toplam {len(self.translated_files)} dosya çevrildi!")
        if errors:
            messagebox.showwarning(
                "Çeviri Tamamlandı",
                f"{len(errors)} dosya çevrilemedi. Detaylar konsola yazdırıldı.",
            )
        
        if last_success_path:
            self.translated_preview.delete("1.0", "end")
            self.translated_preview.insert("1.0", last_translated_content)
            self.middle_right_title.configure(text=f"Çeviri: {os.path.basename(last_success_path)}")
            self.update_translated_stats(last_translated_content)

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
                self.update_translated_stats(translated_content)
                
                print(f"Çevrilmiş dosya seçildi: {clean_filename}")
                print(f"İçerik uzunluğu: {len(translated_content)} karakter")
            else:
                self.translated_preview.delete("1.0", "end")
                self.middle_right_title.configure(text="Çeviri Önizleme")
                print(f"Çevrilmiş dosya bulunamadı: {clean_filename}")
                self.update_translated_stats("")
                
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

        self.update_header_stats()
                                       
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
                self.update_translated_stats("")
                self.update_header_stats()
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

        self.update_match_tag_style(mode)

    def update_match_tag_style(self, mode=None):
        """Dosya ağacı eşleşme etiketi renklerini güncelle"""
        if not hasattr(self, 'file_tree'):
            return

        if mode is None:
            mode = (ctk.get_appearance_mode() or "dark").lower()
        else:
            mode = str(mode).lower()

        if mode == "light":
            match_bg = "#cfe3ff"
            match_fg = "#0f172a"
        else:
            match_bg = "#1f6aa5"
            match_fg = "white"

        self.file_tree.tag_configure("match", background=match_bg, foreground=match_fg)

if __name__ == "__main__":
    app = FileTranslatorApp()
    app.mainloop()
