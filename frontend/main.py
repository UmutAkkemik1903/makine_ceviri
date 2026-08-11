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


# --- Görsel sistem: taş zemin + kömür ray + bakır vurgu (kart paneli değil, atölye) ---
class Tema:
    tuval = "#E6E1D8"
    yuzey = "#FAF8F4"
    yuzey_alt = "#F1EDE4"
    ray = "#171412"
    ray_yazi = "#F5F0E8"
    ray_soluk = "#A8A29E"
    mucur = "#1C1917"
    soluk = "#78716C"
    cizgi = "#D6D0C4"
    vurgu = "#C2410C"
    vurgu_hover = "#9A3412"
    vurgu_yazi = "#FFF7ED"
    basari = "#0F766E"
    tehlikeli = "#B91C1C"
    editor = "#FFFEFB"
    editor_koyu = "#1A1816"
    eslesme_acik = "#FED7AA"
    eslesme_koyu = "#7C2D12"

    @staticmethod
    def font(boyut=13, kalin=False, mono=False):
        agaliga = "Menlo" if mono else "Avenir Next"
        yedek = "Menlo" if mono else "Helvetica Neue"
        try:
            return ctk.CTkFont(family=agaliga, size=boyut, weight="bold" if kalin else "normal")
        except Exception:
            return ctk.CTkFont(family=yedek, size=boyut, weight="bold" if kalin else "normal")


class FileTranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MAKİNE — Dosya Çeviri Atölyesi")
        self.geometry("1480x900")
        self.minsize(1180, 720)
        self.configure(fg_color=Tema.tuval)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        self.current_directory = None
        self.selected_file = None
        self.translated_files = {}
        self.supported_formats = [
            ".txt", ".json", ".xml", ".ini", ".cfg",
            ".properties", ".lang", ".yml", ".yaml",
        ]

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

        self.search_var = tk.StringVar()
        self.search_result_var = tk.StringVar(value="Tüm dosyalar görünür")
        self.folder_badge_text = tk.StringVar(value="Klasör seçilmedi")
        self.translation_badge_text = tk.StringVar(value="0 çıktı")
        self.original_stats_text = tk.StringVar(value="—")
        self.translated_stats_text = tk.StringVar(value="—")

        self.setup_ui()
        self.initialize_translation_client()

    def setup_treeview_style(self, mode="light"):
        """Ağaç stillerini görsel sisteme bağla"""
        style = ttk.Style()
        style.theme_use("clam")
        if mode == "light":
            style.configure(
                "Atolye.Treeview",
                background=Tema.editor,
                foreground=Tema.mucur,
                fieldbackground=Tema.editor,
                rowheight=28,
                borderwidth=0,
                font=("Menlo", 11),
            )
            style.configure(
                "Atolye.Treeview.Heading",
                background=Tema.yuzey_alt,
                foreground=Tema.mucur,
                relief="flat",
                font=("Avenir Next", 11, "bold"),
            )
            style.map(
                "Atolye.Treeview",
                background=[("selected", Tema.vurgu)],
                foreground=[("selected", Tema.vurgu_yazi)],
            )
        else:
            style.configure(
                "Atolye.Treeview",
                background=Tema.editor_koyu,
                foreground="#F5F0E8",
                fieldbackground=Tema.editor_koyu,
                rowheight=28,
                borderwidth=0,
                font=("Menlo", 11),
            )
            style.configure(
                "Atolye.Treeview.Heading",
                background="#2A2522",
                foreground="#F5F0E8",
                relief="flat",
                font=("Avenir Next", 11, "bold"),
            )
            style.map(
                "Atolye.Treeview",
                background=[("selected", Tema.vurgu)],
                foreground=[("selected", Tema.vurgu_yazi)],
            )

    def setup_ui(self):
        """Atölye düzeni: komut şeridi + sol ray + çift editör + durum şeridi"""
        self.grid_columnconfigure(0, weight=0, minsize=300)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        self.create_command_bar()
        self.create_side_rail()
        self.create_workspace()
        self.create_status_bar()

    def create_command_bar(self):
        """Üst komut şeridi — marka + dil çifti + birincil eylemler"""
        bar = ctk.CTkFrame(self, fg_color=Tema.ray, corner_radius=0, height=72)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(1, weight=1)

        marka = ctk.CTkFrame(bar, fg_color="transparent")
        marka.grid(row=0, column=0, padx=(28, 16), pady=14, sticky="w")

        ctk.CTkLabel(
            marka,
            text="MAKİNE",
            font=Tema.font(26, kalin=True),
            text_color=Tema.ray_yazi,
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            marka,
            text="dosya çeviri atölyesi",
            font=Tema.font(12),
            text_color=Tema.ray_soluk,
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        dil_alani = ctk.CTkFrame(bar, fg_color="#221E1B", corner_radius=8)
        dil_alani.grid(row=0, column=1, padx=8, pady=14, sticky="w")

        ctk.CTkLabel(
            dil_alani,
            text="KAYNAK",
            font=Tema.font(10, kalin=True),
            text_color=Tema.ray_soluk,
        ).grid(row=0, column=0, padx=(14, 6), pady=(10, 0), sticky="w")
        ctk.CTkLabel(
            dil_alani,
            text="HEDEF",
            font=Tema.font(10, kalin=True),
            text_color=Tema.ray_soluk,
        ).grid(row=0, column=2, padx=(6, 14), pady=(10, 0), sticky="w")

        self.source_lang_menu = ctk.CTkOptionMenu(
            dil_alani,
            variable=self.source_lang_var,
            values=list(self.source_languages.keys()),
            width=170,
            height=30,
            fg_color="#2F2926",
            button_color=Tema.vurgu,
            button_hover_color=Tema.vurgu_hover,
            dropdown_fg_color="#2F2926",
            dropdown_hover_color=Tema.vurgu,
            text_color=Tema.ray_yazi,
            font=Tema.font(12),
        )
        self.source_lang_menu.grid(row=1, column=0, padx=(14, 6), pady=(2, 12))

        ctk.CTkLabel(
            dil_alani,
            text="→",
            font=Tema.font(18, kalin=True),
            text_color=Tema.vurgu,
        ).grid(row=1, column=1, padx=4, pady=(2, 12))

        self.target_lang_menu = ctk.CTkOptionMenu(
            dil_alani,
            variable=self.target_lang_var,
            values=list(self.target_languages.keys()),
            width=170,
            height=30,
            fg_color="#2F2926",
            button_color=Tema.vurgu,
            button_hover_color=Tema.vurgu_hover,
            dropdown_fg_color="#2F2926",
            dropdown_hover_color=Tema.vurgu,
            text_color=Tema.ray_yazi,
            font=Tema.font(12),
        )
        self.target_lang_menu.grid(row=1, column=2, padx=(6, 14), pady=(2, 12))

        eylemler = ctk.CTkFrame(bar, fg_color="transparent")
        eylemler.grid(row=0, column=2, padx=(8, 24), pady=14, sticky="e")

        self.translate_all_var = ctk.BooleanVar(value=False)
        self.translate_all_checkbox = ctk.CTkCheckBox(
            eylemler,
            text="Tüm desteklenenler",
            variable=self.translate_all_var,
            font=Tema.font(12),
            text_color=Tema.ray_yazi,
            fg_color=Tema.vurgu,
            hover_color=Tema.vurgu_hover,
            border_color=Tema.ray_soluk,
            checkmark_color=Tema.vurgu_yazi,
        )
        self.translate_all_checkbox.grid(row=0, column=0, padx=(0, 14))

        self.translate_btn = ctk.CTkButton(
            eylemler,
            text="Çevir",
            command=self.handle_translation,
            state="disabled",
            height=40,
            width=110,
            corner_radius=6,
            fg_color=Tema.vurgu,
            hover_color=Tema.vurgu_hover,
            text_color=Tema.vurgu_yazi,
            font=Tema.font(14, kalin=True),
        )
        self.translate_btn.grid(row=0, column=1, padx=(0, 8))

        self.export_btn = ctk.CTkButton(
            eylemler,
            text="Dışa Aktar",
            command=self.export_files,
            state="disabled",
            height=40,
            width=120,
            corner_radius=6,
            fg_color="transparent",
            hover_color="#2F2926",
            border_width=1,
            border_color=Tema.ray_soluk,
            text_color=Tema.ray_yazi,
            font=Tema.font(13),
        )
        self.export_btn.grid(row=0, column=2)

        self.update_header_stats()

    def create_side_rail(self):
        """Sol ray: kaynak gezinme + çevrilmiş çıktılar"""
        rail = ctk.CTkFrame(self, fg_color=Tema.ray, corner_radius=0, width=320)
        rail.grid(row=1, column=0, sticky="nsew")
        rail.grid_propagate(False)
        rail.grid_rowconfigure(4, weight=3)
        rail.grid_rowconfigure(7, weight=2)
        rail.grid_columnconfigure(0, weight=1)
        self.left_frame = rail  # geriye uyumluluk

        # — Kaynak bölümü —
        ctk.CTkLabel(
            rail,
            text="KAYNAK AĞACI",
            font=Tema.font(11, kalin=True),
            text_color=Tema.ray_soluk,
            anchor="w",
        ).grid(row=0, column=0, padx=20, pady=(18, 6), sticky="ew")

        ust = ctk.CTkFrame(rail, fg_color="transparent")
        ust.grid(row=1, column=0, padx=16, sticky="ew")
        ust.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            ust,
            text="Klasör Aç",
            command=self.select_folder,
            height=36,
            corner_radius=6,
            fg_color=Tema.vurgu,
            hover_color=Tema.vurgu_hover,
            text_color=Tema.vurgu_yazi,
            font=Tema.font(13, kalin=True),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkButton(
            ust,
            text="Yenile",
            command=self.refresh_current_folder,
            height=36,
            width=72,
            corner_radius=6,
            fg_color="#2F2926",
            hover_color="#3F3733",
            text_color=Tema.ray_yazi,
            font=Tema.font(12),
        ).grid(row=0, column=1)

        self.folder_path_label = ctk.CTkLabel(
            rail,
            textvariable=self.folder_badge_text,
            anchor="w",
            justify="left",
            wraplength=270,
            font=Tema.font(11),
            text_color=Tema.ray_soluk,
        )
        self.folder_path_label.grid(row=2, column=0, padx=20, pady=(10, 4), sticky="ew")

        ara = ctk.CTkFrame(rail, fg_color="transparent")
        ara.grid(row=3, column=0, padx=16, pady=(4, 6), sticky="ew")
        ara.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            ara,
            textvariable=self.search_var,
            placeholder_text="Dosya ara…",
            height=34,
            corner_radius=6,
            border_width=0,
            fg_color="#2F2926",
            text_color=Tema.ray_yazi,
            placeholder_text_color=Tema.ray_soluk,
            font=Tema.font(12),
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.search_entry.bind(
            "<KeyRelease>", lambda e: self.apply_tree_search(self.search_var.get())
        )

        ctk.CTkButton(
            ara,
            text="×",
            width=34,
            height=34,
            corner_radius=6,
            command=self.clear_search_query,
            fg_color="#2F2926",
            hover_color="#3F3733",
            text_color=Tema.ray_yazi,
            font=Tema.font(16),
        ).grid(row=0, column=1)

        ctk.CTkLabel(
            ara,
            textvariable=self.search_result_var,
            anchor="w",
            font=Tema.font(10),
            text_color=Tema.ray_soluk,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        tree_wrap = ctk.CTkFrame(rail, fg_color="#221E1B", corner_radius=8)
        tree_wrap.grid(row=4, column=0, padx=16, pady=(4, 8), sticky="nsew")
        tree_wrap.grid_rowconfigure(0, weight=1)
        tree_wrap.grid_columnconfigure(0, weight=1)

        self.setup_treeview_style("light")
        self.file_tree = ttk.Treeview(
            tree_wrap, show="tree headings", columns=("type",), style="Atolye.Treeview"
        )
        self.file_tree.heading("#0", text="Dosya / klasör")
        self.file_tree.heading("type", text="Tür")
        self.file_tree.column("#0", width=170, stretch=True)
        self.file_tree.column("type", width=90, stretch=False)

        sb = ttk.Scrollbar(tree_wrap, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=sb.set)
        self.file_tree.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        sb.grid(row=0, column=1, sticky="ns", pady=4)
        self.file_tree.bind("<<TreeviewSelect>>", self.on_file_select)
        self.update_match_tag_style("light")

        # — Çıktı bölümü —
        ayirici = ctk.CTkFrame(rail, fg_color="#2F2926", height=1)
        ayirici.grid(row=5, column=0, padx=16, sticky="ew")

        cikti_baslik = ctk.CTkFrame(rail, fg_color="transparent")
        cikti_baslik.grid(row=6, column=0, padx=16, pady=(12, 4), sticky="ew")
        cikti_baslik.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            cikti_baslik,
            text="ÇIKTILAR",
            font=Tema.font(11, kalin=True),
            text_color=Tema.ray_soluk,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            cikti_baslik,
            textvariable=self.translation_badge_text,
            font=Tema.font(11, kalin=True),
            text_color=Tema.vurgu,
        ).grid(row=0, column=1, padx=(0, 8))

        ctk.CTkButton(
            cikti_baslik,
            text="Temizle",
            command=self.clear_translated_files,
            width=64,
            height=26,
            corner_radius=4,
            fg_color="transparent",
            hover_color="#2F2926",
            border_width=1,
            border_color=Tema.ray_soluk,
            text_color=Tema.ray_yazi,
            font=Tema.font(11),
        ).grid(row=0, column=2)

        self.right_frame = ctk.CTkFrame(rail, fg_color="#221E1B", corner_radius=8)
        self.right_frame.grid(row=7, column=0, padx=16, pady=(4, 16), sticky="nsew")
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.translated_tree = ttk.Treeview(
            self.right_frame,
            show="tree headings",
            columns=("status",),
            style="Atolye.Treeview",
        )
        self.translated_tree.heading("#0", text="Dosya")
        self.translated_tree.heading("status", text="Durum")
        self.translated_tree.column("#0", width=170, stretch=True)
        self.translated_tree.column("status", width=80, stretch=False)

        tsb = ttk.Scrollbar(
            self.right_frame, orient="vertical", command=self.translated_tree.yview
        )
        self.translated_tree.configure(yscrollcommand=tsb.set)
        self.translated_tree.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        tsb.grid(row=0, column=1, sticky="ns", pady=4)
        self.translated_tree.bind("<<TreeviewSelect>>", self.on_translated_file_select)

    def create_workspace(self):
        """Ana çalışma alanı: kaynak | çeviri yan yana"""
        alan = ctk.CTkFrame(self, fg_color=Tema.tuval, corner_radius=0)
        alan.grid(row=1, column=1, sticky="nsew")
        alan.grid_columnconfigure(0, weight=1)
        alan.grid_columnconfigure(1, weight=1)
        alan.grid_rowconfigure(0, weight=1)

        # Sol editör
        self.middle_left_frame = ctk.CTkFrame(
            alan, fg_color=Tema.yuzey, corner_radius=0, border_width=0
        )
        self.middle_left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 1))
        self.middle_left_frame.grid_rowconfigure(1, weight=1)
        self.middle_left_frame.grid_columnconfigure(0, weight=1)

        sol_ust = ctk.CTkFrame(self.middle_left_frame, fg_color=Tema.yuzey_alt, corner_radius=0)
        sol_ust.grid(row=0, column=0, sticky="ew")
        sol_ust.grid_columnconfigure(0, weight=1)

        meta = ctk.CTkFrame(sol_ust, fg_color="transparent")
        meta.grid(row=0, column=0, padx=20, pady=14, sticky="w")

        ctk.CTkLabel(
            meta,
            text="KAYNAK",
            font=Tema.font(10, kalin=True),
            text_color=Tema.soluk,
        ).grid(row=0, column=0, sticky="w")
        self.middle_left_title = ctk.CTkLabel(
            meta,
            text="Dosya seçilmedi",
            font=Tema.font(16, kalin=True),
            text_color=Tema.mucur,
        )
        self.middle_left_title.grid(row=1, column=0, sticky="w", pady=(2, 0))

        ctk.CTkButton(
            sol_ust,
            text="Kopyala",
            command=self.copy_original_to_clipboard,
            height=32,
            width=88,
            corner_radius=6,
            fg_color=Tema.mucur,
            hover_color="#44403C",
            text_color=Tema.yuzey,
            font=Tema.font(12),
        ).grid(row=0, column=1, padx=20, pady=14)

        self.original_content = ctk.CTkTextbox(
            self.middle_left_frame,
            wrap="word",
            corner_radius=0,
            border_width=0,
            fg_color=Tema.editor,
            text_color=Tema.mucur,
            font=Tema.font(13, mono=True),
        )
        self.original_content.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.original_content.bind(
            "<KeyRelease>",
            lambda e: self.update_original_stats(
                self.original_content.get("1.0", "end-1c")
            ),
        )

        sol_alt = ctk.CTkFrame(self.middle_left_frame, fg_color=Tema.yuzey_alt, corner_radius=0, height=36)
        sol_alt.grid(row=2, column=0, sticky="ew")
        self.original_stats_label = ctk.CTkLabel(
            sol_alt,
            textvariable=self.original_stats_text,
            anchor="w",
            font=Tema.font(11, mono=True),
            text_color=Tema.soluk,
        )
        self.original_stats_label.pack(side="left", padx=20, pady=8)

        # Sağ editör
        self.middle_right_frame = ctk.CTkFrame(
            alan, fg_color=Tema.yuzey, corner_radius=0
        )
        self.middle_right_frame.grid(row=0, column=1, sticky="nsew")
        self.middle_right_frame.grid_rowconfigure(1, weight=1)
        self.middle_right_frame.grid_columnconfigure(0, weight=1)

        sag_ust = ctk.CTkFrame(self.middle_right_frame, fg_color=Tema.yuzey_alt, corner_radius=0)
        sag_ust.grid(row=0, column=0, sticky="ew")
        sag_ust.grid_columnconfigure(0, weight=1)

        meta2 = ctk.CTkFrame(sag_ust, fg_color="transparent")
        meta2.grid(row=0, column=0, padx=20, pady=14, sticky="w")

        ctk.CTkLabel(
            meta2,
            text="ÇEVİRİ",
            font=Tema.font(10, kalin=True),
            text_color=Tema.soluk,
        ).grid(row=0, column=0, sticky="w")
        self.middle_right_title = ctk.CTkLabel(
            meta2,
            text="Henüz çeviri yok",
            font=Tema.font(16, kalin=True),
            text_color=Tema.mucur,
        )
        self.middle_right_title.grid(row=1, column=0, sticky="w", pady=(2, 0))

        ctk.CTkButton(
            sag_ust,
            text="Kopyala",
            command=self.copy_translated_to_clipboard,
            height=32,
            width=88,
            corner_radius=6,
            fg_color=Tema.basari,
            hover_color="#0D9488",
            text_color="#ECFDF5",
            font=Tema.font(12),
        ).grid(row=0, column=1, padx=20, pady=14)

        self.translated_preview = ctk.CTkTextbox(
            self.middle_right_frame,
            wrap="word",
            corner_radius=0,
            border_width=0,
            fg_color=Tema.editor,
            text_color=Tema.mucur,
            font=Tema.font(13, mono=True),
            state="normal",
        )
        self.translated_preview.grid(row=1, column=0, sticky="nsew")
        self.translated_preview.bind(
            "<KeyRelease>",
            lambda e: self.update_translated_stats(
                self.translated_preview.get("1.0", "end-1c")
            ),
        )

        sag_alt = ctk.CTkFrame(self.middle_right_frame, fg_color=Tema.yuzey_alt, corner_radius=0, height=36)
        sag_alt.grid(row=2, column=0, sticky="ew")
        self.translated_stats_label = ctk.CTkLabel(
            sag_alt,
            textvariable=self.translated_stats_text,
            anchor="w",
            font=Tema.font(11, mono=True),
            text_color=Tema.soluk,
        )
        self.translated_stats_label.pack(side="left", padx=20, pady=8)

    def create_status_bar(self):
        """Alt durum şeridi"""
        self.bottom_frame = ctk.CTkFrame(self, fg_color=Tema.yuzey, corner_radius=0, height=48)
        self.bottom_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.bottom_frame.grid_propagate(False)
        self.bottom_frame.grid_columnconfigure(2, weight=1)

        self.theme_switch = ctk.CTkSwitch(
            self.bottom_frame,
            text="Koyu yüzey",
            command=self.toggle_theme,
            font=Tema.font(12),
            text_color=Tema.mucur,
            progress_color=Tema.vurgu,
            button_color=Tema.mucur,
            button_hover_color=Tema.vurgu,
        )
        self.theme_switch.grid(row=0, column=0, padx=(20, 12), pady=10)

        self.progress_bar = ctk.CTkProgressBar(
            self.bottom_frame,
            width=160,
            height=8,
            corner_radius=4,
            progress_color=Tema.vurgu,
            fg_color=Tema.cizgi,
        )
        self.progress_bar.grid(row=0, column=1, padx=8, pady=10)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            self.bottom_frame,
            text="Klasör açarak başlayın",
            anchor="w",
            font=Tema.font(12),
            text_color=Tema.soluk,
        )
        self.status_label.grid(row=0, column=2, padx=12, pady=10, sticky="ew")

        yardim = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        yardim.grid(row=0, column=3, padx=(8, 16), pady=8, sticky="e")

        ctk.CTkButton(
            yardim,
            text="Kılavuz",
            command=self.open_usage_guide,
            height=28,
            width=80,
            corner_radius=4,
            fg_color="transparent",
            hover_color=Tema.yuzey_alt,
            border_width=1,
            border_color=Tema.cizgi,
            text_color=Tema.mucur,
            font=Tema.font(11),
        ).grid(row=0, column=0, padx=(0, 6))

        ctk.CTkButton(
            yardim,
            text="Günlük",
            command=self.open_translation_log,
            height=28,
            width=80,
            corner_radius=4,
            fg_color="transparent",
            hover_color=Tema.yuzey_alt,
            border_width=1,
            border_color=Tema.cizgi,
            text_color=Tema.mucur,
            font=Tema.font(11),
        ).grid(row=0, column=1)


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
            self.folder_badge_text.set(f"{folder_name}\n{self.current_directory}")
        else:
            self.folder_badge_text.set("Klasör seçilmedi")

        translated_count = len(self.translated_files)
        self.translation_badge_text.set(f"{translated_count} çıktı")

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
            self.search_result_var.set("Tüm dosyalar görünür")

    def _iter_tree_items(self, tree, parent=""):
        """Treeview elemanları üzerinde dolaş"""
        for item in tree.get_children(parent):
            yield item
            yield from self._iter_tree_items(tree, item)

    def update_original_stats(self, content, encoding=None):
        """Orijinal içerik istatistiklerini güncelle"""
        content = content or ""
        if not content:
            self.original_stats_text.set("—")
            return
        line_count = content.count("\n")
        if not content.endswith("\n"):
            line_count += 1
        char_count = len(content)
        if encoding:
            encoding_display = encoding.upper() if isinstance(encoding, str) else str(encoding)
            info = f"{line_count} satır  ·  {char_count} karakter  ·  {encoding_display}"
        else:
            info = f"{line_count} satır  ·  {char_count} karakter"
        self.original_stats_text.set(info)

    def update_translated_stats(self, content):
        """Çeviri önizleme istatistiklerini güncelle"""
        content = content or ""
        if not content:
            self.translated_stats_text.set("—")
            return
        line_count = content.count("\n")
        if not content.endswith("\n"):
            line_count += 1
        char_count = len(content)
        self.translated_stats_text.set(f"{line_count} satır  ·  {char_count} karakter")

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
        
    def select_folder(self):
        """Klasör seçme"""
        # Proje kökünü varsayılan başlangıç dizini yap (frontend/ bir üstü)
        proje_koku = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        folder_path = filedialog.askdirectory(
            title="Çeviri için klasör seçin",
            initialdir=proje_koku
        )
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
        self.search_result_var.set("Tüm dosyalar görünür")
        
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
                    self.middle_left_title.configure(text="Dosya seçilmedi")
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
                self.middle_left_title.configure(text="Dosya seçilmedi")
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
        # Büyük dosya eşiği: 200 KB üstü için önizleme modu
        BUYUK_DOSYA_ESIGI = 200_000
        try:
            print(f"Dosya yükleniyor: {file_path}")

            if not os.path.exists(file_path):
                self.status_label.configure(text="Dosya bulunamadı!")
                return

            if not os.path.isfile(file_path):
                self.status_label.configure(text="Bu bir dosya değil!")
                return

            dosya_boyutu = os.path.getsize(file_path)

            if dosya_boyutu > BUYUK_DOSYA_ESIGI:
                # Büyük dosya: sadece ilk 4KB ile encoding algıla, widget'a tam içerik koyma
                with open(file_path, 'rb') as f:
                    orneklem = f.read(4096)
                result = chardet.detect(orneklem)
                encoding = result['encoding'] or 'utf-8'
                self._large_file_encoding = encoding

                ozet = (
                    f"[BÜYÜK DOSYA - ÖNİZLEME DEVRE DIŞI]\n"
                    f"Dosya: {os.path.basename(file_path)}\n"
                    f"Boyut: {dosya_boyutu / 1024:.1f} KB\n"
                    f"Kodlama: {encoding}\n\n"
                    f"Dosya çok büyük olduğu için önizleme gösterilmiyor.\n"
                    f"'Çevir' butonuna basarak çeviriyi başlatabilirsiniz."
                )
                self.original_content.delete("1.0", "end")
                self.original_content.insert("1.0", ozet)
                self.middle_left_title.configure(text=f"{os.path.basename(file_path)}  ·  büyük dosya")
                self.update_original_stats(ozet, encoding)
                print(f"Büyük dosya modu: {dosya_boyutu:,} bayt — önizleme atlandı")
            else:
                # Normal dosya: tam içeriği yükle
                self._large_file_encoding = None
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'

                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()

                self.original_content.delete("1.0", "end")
                self.original_content.insert("1.0", content)
                self.middle_left_title.configure(text=os.path.basename(file_path))
                self.update_original_stats(content, encoding)
                print(f"Dosya yüklendi: {len(content):,} karakter")

        except Exception as e:
            error_msg = f"Dosya okunamadı: {str(e)}\nDosya yolu: {file_path}"
            print(error_msg)
            messagebox.showerror("Hata", error_msg)
            self.status_label.configure(text="Dosya okuma hatası!")
            self.update_original_stats("")
            
    def translate_file(self):
        """Dosya çevirisi - ağır işlemi arka plan thread'inde çalıştır"""
        if not self.selected_file:
            return

        self.progress_bar.set(0.1)
        self.status_label.configure(text="Çeviri yapılıyor...")
        self.translate_btn.configure(state="disabled")

        dosya_yolu = self.selected_file

        # Büyük dosyada widget yerine diskten oku
        buyuk_dosya_modu = getattr(self, '_large_file_encoding', None) is not None
        if buyuk_dosya_modu:
            encoding = self._large_file_encoding
            try:
                with open(dosya_yolu, 'r', encoding=encoding) as f:
                    content = f.read()
            except Exception as hata:
                self._ceviri_hatasi(hata)
                return
        else:
            content = self.original_content.get("1.0", "end-1c")

        def _arka_planda_cevir():
            try:
                cevrilmis = self._perform_translation(content, dosya_yolu)
                self.after(0, lambda: self._ceviri_tamamlandi(cevrilmis, dosya_yolu))
            except Exception as hata:
                self.after(0, lambda: self._ceviri_hatasi(hata))

        threading.Thread(target=_arka_planda_cevir, daemon=True).start()

    def _ceviri_tamamlandi(self, translated, dosya_yolu):
        """Arka plan çevirisi bitince UI'yi güncelle"""
        self.translated_preview.delete("1.0", "end")
        self.translated_preview.insert("1.0", translated)
        self.middle_right_title.configure(text=os.path.basename(dosya_yolu))
        self.update_translated_stats(translated)

        self.translated_files[dosya_yolu] = translated
        self.update_translated_files_tree()
        self.update_header_stats()

        self.progress_bar.set(1.0)
        self.export_btn.configure(state="normal")
        self.translate_btn.configure(state="normal")
        self.status_label.configure(text="Çeviri tamamlandı!")

        filename = os.path.basename(dosya_yolu)
        for item in self.translated_tree.get_children():
            if filename in self.translated_tree.item(item, "text"):
                self.translated_tree.selection_set(item)
                self.on_translated_file_select(None)
                break

        self.after(2000, lambda: self.progress_bar.set(0))

    def _ceviri_hatasi(self, hata):
        """Arka plan çevirisi hata verince UI'yi güncelle"""
        self.progress_bar.set(0)
        self.translate_btn.configure(state="normal")
        self.status_label.configure(text="Çeviri başarısız!")
        messagebox.showerror("Çeviri Hatası", str(hata))
        
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

    # Her JSON çeviri oturumunda kullanılacak karakter bütçesi
    # DeepL ücretsiz tier: 500,000 / ay — güvenli marj bırakarak 490,000 ayarlandı
    KARAKTER_LIMITI = 490_000

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

        if isinstance(data, str):
            translated = self.translation_client.translate_text(
                data,
                target_lang=target_code,
                source_lang=source_code,
                preserve_formatting=True,
            )
            if isinstance(translated, list):
                translated = translated[0] if translated else ""
            result = json.dumps(translated, ensure_ascii=False, indent=4)
            if trailing_newline and not result.endswith('\n'):
                result += '\n'
            return result

        # Liste ise her kaydın karakter maliyetini hesapla, bütçe dolana kadar çevir
        if isinstance(data, list):
            references = self._butce_dahilinde_referanslar_topla(data, target_code)
        else:
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

    # Hedef dil karakterleri — her dile özgü ünik karakterler (devam çevirisi tespiti için)
    _HEDEF_DIL_KARAKTERLERI = {
        'TR': frozenset('ğüşıöçĞÜŞİÖÇ'),
        'DE': frozenset('äöüÄÖÜß'),
        'FR': frozenset('éàêèùûîôâœæçÉÀÊÈÙÛÎÔÂŒÆÇ'),
        'ES': frozenset('áéíóúüñ¿¡ÁÉÍÓÚÜÑ'),
        'PT-BR': frozenset('ãõáéíóúâêôàçÃÕÁÉÍÓÚÂÊÔÀÇ'),
        'PT-PT': frozenset('ãõáéíóúâêôàçÃÕÁÉÍÓÚÂÊÔÀÇ'),
        'IT': frozenset('àèéìíîóòùúÀÈÉÌÍÎÓÒÙÚ'),
        'PL': frozenset('ąćęłńóśźżĄĆĘŁŃÓŚŹŻ'),
        'RU': frozenset('абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
                        'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'),
    }

    def _kayit_hedef_dilde_mi(self, item, target_code):
        """Kaydın çevrilebilir alanları hedef dil karakterleri içeriyor mu?
        Evet ise bu kayıt daha önce çevrilmiş sayılır."""
        hedef_chars = self._HEDEF_DIL_KARAKTERLERI.get(target_code, frozenset())

        # CJK (Japonca, Çince, Korece) — Unicode aralığı kontrolU
        cjk_hedef = target_code in ('JA', 'ZH', 'KO')

        if not hedef_chars and not cjk_hedef:
            return False  # Bilinmeyen dil — atla

        refs = []
        if isinstance(item, (dict, list)):
            self._collect_json_string_nodes(item, refs)
        elif isinstance(item, str):
            refs = [(None, None, item)]

        for (_, _, value) in refs:
            if hedef_chars and any(c in hedef_chars for c in value):
                return True
            if cjk_hedef and any('\u4e00' <= c <= '\u9fff' or '\u3040' <= c <= '\u30ff' for c in value):
                return True
        return False

    def _butce_dahilinde_referanslar_topla(self, liste, target_code=None):
        """Her öğenin çeviri durumunu ve karakter maliyetini hesapla.
        Zaten çevrilmiş olanları atla, kalanı bütçe dahilinde çevir.
        Dosya yeniden yüklendiğinde kaldığı yerden devam eder."""
        butce_kalan = self.KARAKTER_LIMITI
        referanslar = []
        zaten_cevrilmis = 0
        cevrilecek = 0
        butce_yetersiz = 0

        for i, item in enumerate(liste):
            # Hedef dil karakterleri varsa bu kayıt daha önce çevrilmiş — atla
            if target_code and self._kayit_hedef_dilde_mi(item, target_code):
                zaten_cevrilmis += 1
                continue

            # Bu öğenin çevrilebilir karakter maliyetini hesapla
            item_refs = []
            if isinstance(item, (dict, list)):
                self._collect_json_string_nodes(item, item_refs)
            elif isinstance(item, str) and not self._is_untranslatable_string(item):
                item_refs.append((liste, i, item))

            item_karakter = sum(len(v) for (_, _, v) in item_refs)
            if item_karakter == 0:
                continue  # Çevrilebilir metin yok

            if butce_kalan >= item_karakter:
                butce_kalan -= item_karakter
                referanslar.extend(item_refs)
                cevrilecek += 1
            else:
                butce_yetersiz += 1

        toplam = len(liste)
        print(f"[INFO] Toplam: {toplam} — "
              f"Zaten çevrilmiş: {zaten_cevrilmis}, "
              f"Bu çalışmada çevrilecek: {cevrilecek}, "
              f"Bütçe yetersiz: {butce_yetersiz}")
        return referanslar

    # Anahtar ismine göre hiçbir zaman çevrilmeyecek JSON alanları
    # contentHtml -> contentText'in HTML kopyası, fazladan karakter
    # $date       -> ISO zaman damgası
    # components  -> V, S, M gibi oyun mekaniği kodları
    _ATLANACAK_JSON_ANAHTARLARI = frozenset({'contentHtml', '$date', 'components'})

    def _is_untranslatable_string(self, value: str) -> bool:
        """URL, ObjectId, slug ve ISO tarih gibi çevrilmemesi gereken değerleri filtrele"""
        import re
        if not value or not value.strip():
            return True
        # URL değerleri çevrilmez
        if value.startswith(('http://', 'https://')):
            return True
        # MongoDB ObjectId (24 hex karakter)
        if re.match(r'^[0-9a-f]{24}$', value):
            return True
        # ISO tarih/zaman damgası (2024-01-15T00:00:00.000Z vb.)
        if re.match(r'^\d{4}-\d{2}-\d{2}', value):
            return True
        # Boşluk içermeyen saf slug/kod değerleri (acid-splash, EN_US vb.)
        if re.match(r'^[a-z0-9][a-z0-9_\-]*$', value) and ' ' not in value and len(value) < 60:
            return True
        return False

    def _collect_json_string_nodes(self, obj, references):
        if isinstance(obj, dict):
            for key, value in obj.items():
                # Anahtar ismine göre bazı alanları tamamen atla
                if key in self._ATLANACAK_JSON_ANAHTARLARI:
                    continue
                if isinstance(value, str):
                    if not self._is_untranslatable_string(value):
                        references.append((obj, key, value))
                elif isinstance(value, (dict, list)):
                    self._collect_json_string_nodes(value, references)
        elif isinstance(obj, list):
            for index, item in enumerate(obj):
                if isinstance(item, str):
                    if not self._is_untranslatable_string(item):
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
            self.middle_right_title.configure(text=os.path.basename(last_success_path))
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
                self.middle_right_title.configure(text=clean_filename)
                self.update_translated_stats(translated_content)
                
                print(f"Çevrilmiş dosya seçildi: {clean_filename}")
                print(f"İçerik uzunluğu: {len(translated_content)} karakter")
            else:
                self.translated_preview.delete("1.0", "end")
                self.middle_right_title.configure(text="Henüz çeviri yok")
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
                                       values=("hazır",))
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
                self.middle_right_title.configure(text="Henüz çeviri yok")
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
        """Açık/koyu yüzey değişimi"""
        if self.theme_switch.get():
            ctk.set_appearance_mode("dark")
            self.configure(fg_color="#12100E")
            self.update_treeview_style("dark")
            self._yuzeyleri_koyu_yap()
        else:
            ctk.set_appearance_mode("light")
            self.configure(fg_color=Tema.tuval)
            self.update_treeview_style("light")
            self._yuzeyleri_acik_yap()

    def _yuzeyleri_acik_yap(self):
        """Açık atölye paletini uygula"""
        if hasattr(self, "middle_left_frame"):
            self.middle_left_frame.configure(fg_color=Tema.yuzey)
            self.middle_right_frame.configure(fg_color=Tema.yuzey)
            self.original_content.configure(fg_color=Tema.editor, text_color=Tema.mucur)
            self.translated_preview.configure(fg_color=Tema.editor, text_color=Tema.mucur)
            self.bottom_frame.configure(fg_color=Tema.yuzey)
            self.status_label.configure(text_color=Tema.soluk)
            self.middle_left_title.configure(text_color=Tema.mucur)
            self.middle_right_title.configure(text_color=Tema.mucur)

    def _yuzeyleri_koyu_yap(self):
        """Koyu atölye paletini uygula"""
        if hasattr(self, "middle_left_frame"):
            self.middle_left_frame.configure(fg_color="#1A1816")
            self.middle_right_frame.configure(fg_color="#1A1816")
            self.original_content.configure(fg_color=Tema.editor_koyu, text_color="#F5F0E8")
            self.translated_preview.configure(fg_color=Tema.editor_koyu, text_color="#F5F0E8")
            self.bottom_frame.configure(fg_color="#171412")
            self.status_label.configure(text_color=Tema.ray_soluk)
            self.middle_left_title.configure(text_color="#F5F0E8")
            self.middle_right_title.configure(text_color="#F5F0E8")

    def update_treeview_style(self, mode):
        """TreeView stillerini tema değişikliğine göre güncelle"""
        self.setup_treeview_style(mode)
        if hasattr(self, "file_tree"):
            self.file_tree.update()
        if hasattr(self, "translated_tree"):
            self.translated_tree.update()
        self.update_match_tag_style(mode)

    def update_match_tag_style(self, mode=None):
        """Dosya ağacı eşleşme etiketi renklerini güncelle"""
        if not hasattr(self, "file_tree"):
            return
        if mode is None:
            mode = (ctk.get_appearance_mode() or "light").lower()
        else:
            mode = str(mode).lower()
        if mode == "light":
            self.file_tree.tag_configure(
                "match", background=Tema.eslesme_acik, foreground=Tema.mucur
            )
        else:
            self.file_tree.tag_configure(
                "match", background=Tema.eslesme_koyu, foreground="#FED7AA"
            )


if __name__ == "__main__":
    app = FileTranslatorApp()
    app.mainloop()
