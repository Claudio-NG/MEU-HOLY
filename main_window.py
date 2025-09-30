from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog, QComboBox, QSpinBox, QMessageBox, QSplitter
from PyQt6.QtCore import Qt
from themes import DEFAULT_THEMES

class MainWindow(QMainWindow):
    def __init__(self, song_svc, setlist_svc, theme_svc, projector, stage, timer_svc, media_svc, base_cfg):
        super().__init__()
        self.song_svc = song_svc
        self.setlist_svc = setlist_svc
        self.theme_svc = theme_svc
        self.projector = projector
        self.stage = stage
        self.timer_svc = timer_svc
        self.media_svc = media_svc
        self.base, self.cfg, self.save_cfg = base_cfg
        self.setWindowTitle("Holyrics-Python MVP — Raiz")
        self.resize(1500, 860)
        self.root = QWidget(); self.setCentralWidget(self.root)
        main = QHBoxLayout(self.root)
        splitter = QSplitter(Qt.Orientation.Horizontal); main.addWidget(splitter)
        leftw = QWidget(); left = QVBoxLayout(leftw)
        midw = QWidget(); mid = QVBoxLayout(midw)
        rightw = QWidget(); right = QVBoxLayout(rightw)
        splitter.addWidget(leftw); splitter.addWidget(midw); splitter.addWidget(rightw)
        splitter.setSizes([380, 640, 480])
        # Música
        self.song_list = QListWidget()
        self.song_search = QLineEdit(); self.song_search.setPlaceholderText("Buscar músicas...")
        self.song_title = QLineEdit()
        self.song_author = QLineEdit()
        self.song_tags = QLineEdit()
        self.lyric_block = QTextEdit()
        self.btn_add_block = QPushButton("Adicionar Bloco")
        self.blocks_view = QListWidget()
        self.btn_save_song = QPushButton("Salvar Música")
        left.addWidget(QLabel("Filtro")); left.addWidget(self.song_search); left.addWidget(self.song_list)
        mid.addWidget(QLabel("Título")); mid.addWidget(self.song_title)
        mid.addWidget(QLabel("Autor/Tags")); mid.addWidget(self.song_author); mid.addWidget(self.song_tags)
        mid.addWidget(QLabel("Conteúdo do Bloco")); mid.addWidget(self.lyric_block); mid.addWidget(self.btn_add_block)
        mid.addWidget(QLabel("Blocos")); mid.addWidget(self.blocks_view); mid.addWidget(self.btn_save_song)
        # Controles Projeto
        self.btn_project_show = QPushButton("Projetar Bloco Selecionado")
        self.btn_project_clear = QPushButton("Limpar Tela")
        self.theme_select = QComboBox(); self.btn_apply_theme = QPushButton("Aplicar Tema")
        self.bg_pick = QPushButton("Escolher Fundo (Imagem/Vídeo)")
        self.timer_min = QSpinBox(); self.timer_min.setRange(0, 180)
        self.timer_sec = QSpinBox(); self.timer_sec.setRange(0, 59)
        self.btn_timer_start = QPushButton("Iniciar Timer"); self.btn_timer_stop = QPushButton("Parar Timer")
        right.addWidget(QLabel("Tema")); right.addWidget(self.theme_select); right.addWidget(self.btn_apply_theme)
        right.addWidget(self.bg_pick); right.addWidget(self.btn_project_show); right.addWidget(self.btn_project_clear)
        right.addWidget(QLabel("Timer MM:SS"))
        hb = QHBoxLayout(); hbw = QWidget(); hbw.setLayout(hb); hb.addWidget(self.timer_min); hb.addWidget(self.timer_sec)
        right.addWidget(hbw); right.addWidget(self.btn_timer_start); right.addWidget(self.btn_timer_stop)
        # Monitores
        right.addWidget(QLabel("Saídas"))
        self.cmb_projector = QComboBox(); self.cmb_stage = QComboBox()
        self.btn_open_proj = QPushButton("Abrir Projetor"); self.btn_close_proj = QPushButton("Fechar Projetor")
        self.btn_open_stage = QPushButton("Abrir Palco"); self.btn_close_stage = QPushButton("Fechar Palco")
        right.addWidget(QLabel("Monitor Projetor")); right.addWidget(self.cmb_projector)
        right.addWidget(QLabel("Monitor Palco")); right.addWidget(self.cmb_stage)
        right.addWidget(self.btn_open_proj); right.addWidget(self.btn_close_proj)
        right.addWidget(self.btn_open_stage); right.addWidget(self.btn_close_stage)
        # Mídias
        right.addWidget(QLabel("Pastas de Mídia"))
        self.btn_pick_audio = QPushButton("Selecionar Pasta Áudio"); self.btn_pick_video = QPushButton("Selecionar Pasta Vídeo"); self.btn_pick_image = QPushButton("Selecionar Pasta Imagens")
        right.addWidget(self.btn_pick_audio); right.addWidget(self.btn_pick_video); right.addWidget(self.btn_pick_image)
        right.addWidget(QLabel("Áudio")); self.list_audio = QListWidget(); right.addWidget(self.list_audio)
        right.addWidget(QLabel("Vídeo")); self.list_video = QListWidget(); right.addWidget(self.list_video)
        right.addWidget(QLabel("Imagens")); self.list_images = QListWidget(); right.addWidget(self.list_images)
        # Link remoto
        self.lbl_remote = QLabel(""); right.addWidget(self.lbl_remote)
        # Conexões
        self.blocks = []; self.song_id = None
        self.song_search.textChanged.connect(self.refresh_songs)
        self.song_list.itemSelectionChanged.connect(self.on_select_song)
        self.btn_add_block.clicked.connect(self.add_block)
        self.blocks_view.itemDoubleClicked.connect(self.project_block)
        self.btn_save_song.clicked.connect(self.save_song)
        self.btn_project_show.clicked.connect(self.project_selected_block)
        self.btn_project_clear.clicked.connect(self.clear_projector)
        self.btn_apply_theme.clicked.connect(self.apply_theme)
        self.bg_pick.clicked.connect(self.pick_bg_file)
        self.btn_timer_start.clicked.connect(self.start_timer)
        self.btn_timer_stop.clicked.connect(self.stop_timer)
        self.btn_pick_audio.clicked.connect(self.pick_audio_dir)
        self.btn_pick_video.clicked.connect(self.pick_video_dir)
        self.btn_pick_image.clicked.connect(self.pick_image_dir)
        self.list_audio.itemDoubleClicked.connect(self.play_audio_item)
        self.list_video.itemDoubleClicked.connect(self.play_video_item)
        self.list_images.itemDoubleClicked.connect(self.play_image_item)
        self.btn_open_proj.clicked.connect(self.open_projector)
        self.btn_close_proj.clicked.connect(self.close_projector)
        self.btn_open_stage.clicked.connect(self.open_stage)
        self.btn_close_stage.clicked.connect(self.close_stage)
        # Carregamento inicial
        self.load_default_themes(); self.refresh_songs(); self.refresh_media_lists(); self.load_screens(); self.update_remote_label(); self.apply_theme_default()

    def load_screens(self):
        from PyQt6.QtWidgets import QApplication
        self.cmb_projector.clear(); self.cmb_stage.clear()
        for i, s in enumerate(QApplication.instance().screens()):
            self.cmb_projector.addItem(f"{i} — {s.name()}", i)
            self.cmb_stage.addItem(f"{i} — {s.name()}", i)
        self.cmb_projector.setCurrentIndex(self.cfg.get("projector_screen_index", 0))
        self.cmb_stage.setCurrentIndex(self.cfg.get("stage_screen_index", 0))

    def update_remote_label(self):
        port = self.cfg.get("server_port", 8765)
        self.lbl_remote.setText(f"Remote: http://localhost:{port}/  |  Health: http://localhost:{port}/health")

    def load_default_themes(self):
        if not self.theme_svc.list_themes():
            for t in DEFAULT_THEMES:
                self.theme_svc.create_theme(t["name"], t["font_family"], t["font_size"], t["color"], t["stroke_color"], t["stroke_width"], t["align"], t["valign"], t["bg_type"], t["bg_value"])
        self.theme_select.clear()
        for t in self.theme_svc.list_themes():
            self.theme_select.addItem(t["name"], t["id"])

    def apply_theme_default(self):
        active_id = self.cfg.get("active_theme_id")
        if active_id is None and self.theme_select.count() > 0:
            active_id = self.theme_select.itemData(0)
        if active_id is not None:
            t = self.theme_svc.get_theme(int(active_id))
            if t:
                self.projector.apply_theme(t)

    def refresh_songs(self):
        self.song_list.clear()
        q = self.song_search.text().strip()
        for s in self.song_svc.list_songs(q):
            self.song_list.addItem(f"{s['id']:04d} • {s['title']}")

    def on_select_song(self):
        sel = self.song_list.selectedItems()
        if not sel:
            return
        sid = int(sel[0].text().split("•")[0].strip())
        s = self.song_svc.get_song(sid)
        if not s:
            return
        self.song_id = s["id"]
        self.song_title.setText(s["title"])
        self.song_author.setText(s.get("author",""))
        self.song_tags.setText(s.get("tags",""))
        self.blocks = s.get("blocks", [])
        self.refresh_blocks()

    def add_block(self):
        cnt = self.lyric_block.toPlainText().strip()
        if not cnt:
            return
        label = f"B{len(self.blocks)+1}"
        self.blocks.append({"label": label, "content": cnt})
        self.lyric_block.clear(); self.refresh_blocks()

    def refresh_blocks(self):
        self.blocks_view.clear()
        for i, b in enumerate(self.blocks):
            self.blocks_view.addItem(f"{i+1:02d} • {b.get('label','')}")

    def save_song(self):
        title = self.song_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Atenção", "Informe o título.")
            return
        if self.song_id is None:
            self.song_id = self.song_svc.create_song(title, self.song_author.text().strip(), "", self.song_tags.text().strip())
        self.song_svc.upsert_lyric_blocks(self.song_id, [{"label": b.get("label",""), "content": b.get("content","")} for b in self.blocks])
        QMessageBox.information(self, "OK", "Música salva.")
        self.refresh_songs()

    def project_block(self, item):
        idx = self.blocks_view.row(item)
        if 0 <= idx < len(self.blocks):
            self.projector.set_text(self.blocks[idx]["content"])
            nxt = self.blocks[idx+1]["content"] if idx+1 < len(self.blocks) else ""
            self.stage.set_now_next(self.blocks[idx]["content"], nxt)

    def project_selected_block(self):
        sel = self.blocks_view.selectedItems()
        if sel:
            self.project_block(sel[0])

    def clear_projector(self):
        self.projector.set_text("")
        self.stage.set_now_next("","")

    def apply_theme(self):
        theme_id = self.theme_select.currentData()
        t = self.theme_svc.get_theme(theme_id)
        if t:
            self.projector.apply_theme(t)
            self.cfg["active_theme_id"] = theme_id
            self.save_cfg(self.base, self.cfg)

    def pick_bg_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Escolher fundo", "", "Mídia (*.png *.jpg *.jpeg *.webp *.bmp *.mp4 *.mov *.mkv *.avi *.webm)")
        if not path:
            return
        kind = self.media_svc.classify(path)
        if kind == "image":
            self.projector.play_media_background("image", path)
        elif kind == "video":
            self.projector.play_media_background("video", path)

    def start_timer(self):
        total = self.timer_min.value()*60 + self.timer_sec.value()
        self.timer_svc.start(total)

    def stop_timer(self):
        self.timer_svc.stop()

    def pick_audio_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Áudio")
        if d:
            self.cfg["audio_dir"] = d
            self.media_svc.set_dirs(self.cfg.get("audio_dir",""), self.cfg.get("video_dir",""), self.cfg.get("image_dir",""))
            self.save_cfg(self.base, self.cfg)
            self.refresh_media_lists()

    def pick_video_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Vídeo")
        if d:
            self.cfg["video_dir"] = d
            self.media_svc.set_dirs(self.cfg.get("audio_dir",""), self.cfg.get("video_dir",""), self.cfg.get("image_dir",""))
            self.save_cfg(self.base, self.cfg)
            self.refresh_media_lists()

    def pick_image_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Imagens")
        if d:
            self.cfg["image_dir"] = d
            self.media_svc.set_dirs(self.cfg.get("audio_dir",""), self.cfg.get("video_dir",""), self.cfg.get("image_dir",""))
            self.save_cfg(self.base, self.cfg)
            self.refresh_media_lists()

    def refresh_media_lists(self):
        self.list_audio.clear(); self.list_video.clear(); self.list_images.clear()
        for p in self.media_svc.list_audio(): self.list_audio.addItem(p)
        for p in self.media_svc.list_video(): self.list_video.addItem(p)
        for p in self.media_svc.list_images(): self.list_images.addItem(p)

    def play_audio_item(self, item):
        self.projector.play_audio(item.text())

    def play_video_item(self, item):
        self.projector.play_media_background("video", item.text())

    def play_image_item(self, item):
        self.projector.play_media_background("image", item.text())

    def open_projector(self):
        idx = self.cmb_projector.currentData()
        self.cfg["projector_screen_index"] = idx
        self.save_cfg(self.base, self.cfg)
        self.projector.open_on_screen(idx)

    def close_projector(self):
        self.projector.close_projector()

    def open_stage(self):
        idx = self.cmb_stage.currentData()
        self.cfg["stage_screen_index"] = idx
        self.save_cfg(self.base, self.cfg)
        self.stage.open_on_screen(idx)

    def close_stage(self):
        self.stage.close_stage()