from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QUrl
from PyQt6.QtGui import QFont, QImage, QPixmap, QPalette, QColor
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
import os

def find_screen(app: QApplication, index: int):
    screens = app.screens()
    if not screens:
        return None
    if index < 0 or index >= len(screens):
        return screens[-1]
    return screens[index]

class ProjectorWindow(QWidget):
    def __init__(self, theme_service, timer_service, media_service):
        super().__init__()
        self.theme_service = theme_service
        self.timer_service = timer_service
        self.media_service = media_service
        self.current_theme = None
        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.fade = QPropertyAnimation(self.opacity, b"opacity", self)
        self.fade.setDuration(350)
        self.fade.setStartValue(0.0)
        self.fade.setEndValue(1.0)
        self.text = QLabel("", self)
        self.text.setWordWrap(True)
        self.text.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.timer_label = QLabel("", self)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.video_widget = QVideoWidget(self)
        self.video_widget.hide()
        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.video_widget)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0,0,0,0)
        lay.addWidget(self.text)
        lay.addWidget(self.timer_label)
        self.bg_mode = ("solid", "#000000")
        self.ticker = QTimer(self)
        self.ticker.timeout.connect(self.on_tick)
        self.ticker.start(1000)
        self.hide()

    def open_on_screen(self, screen_index: int):
        s = find_screen(QApplication.instance(), screen_index)
        if s:
            g = s.geometry()
            self.setGeometry(g)
            self.showFullScreen()
            self.raise_()

    def close_projector(self):
        self.hide()

    def apply_theme(self, theme: dict):
        self.current_theme = theme
        self.text.setStyleSheet(f"color: {theme['color']};")
        f = QFont(theme["font_family"], int(theme["font_size"]))
        self.text.setFont(f)
        align_map = {"left": Qt.AlignmentFlag.AlignLeft, "center": Qt.AlignmentFlag.AlignHCenter, "right": Qt.AlignmentFlag.AlignRight}
        valign_map = {"top": Qt.AlignmentFlag.AlignTop, "middle": Qt.AlignmentFlag.AlignVCenter, "bottom": Qt.AlignmentFlag.AlignBottom}
        a = align_map.get(theme["align"], Qt.AlignmentFlag.AlignHCenter) | valign_map.get(theme["valign"], Qt.AlignmentFlag.AlignVCenter)
        self.text.setAlignment(a)
        self.apply_background(theme.get("bg_type","solid"), theme.get("bg_value","#0B121A"))

    def apply_background(self, bg_type: str, bg_value: str):
        self.video_widget.hide()
        self.player.stop()
        if bg_type == "solid":
            pal = self.palette()
            pal.setColor(QPalette.ColorRole.Window, QColor(bg_value))
            self.setAutoFillBackground(True)
            self.setPalette(pal)
        elif bg_type == "image":
            if os.path.exists(bg_value):
                img = QImage(bg_value)
                pix = QPixmap.fromImage(img).scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                pal = self.palette()
                pal.setBrush(QPalette.ColorRole.Window, pix)
                self.setPalette(pal)
                self.setAutoFillBackground(True)
        elif bg_type == "video":
            if os.path.exists(bg_value):
                self.video_widget.show()
                self.player.setSource(QUrl.fromLocalFile(bg_value))
                self.player.play()

    def set_text(self, s: str):
        self.text.setText(s)
        self.fade.stop()
        self.opacity.setOpacity(0.0)
        self.fade.start()

    def on_tick(self):
        if self.timer_service.running:
            v = self.timer_service.value()
            mm = v // 60
            ss = v % 60
            self.timer_label.setText(f"{mm:02d}:{ss:02d}")
            self.timer_service.tick()
        else:
            self.timer_label.setText("")

    def play_media_background(self, kind: str, path: str):
        if kind == "image":
            self.apply_background("image", path)
        elif kind == "video":
            self.apply_background("video", path)
        else:
            self.apply_background("solid", "#0B121A")

    def play_audio(self, path: str):
        self.player.stop()
        self.video_widget.hide()
        self.player.setSource(QUrl.fromLocalFile(path))
        self.player.play()

class StageDisplayWindow(QWidget):
    def __init__(self, timer_service):
        super().__init__()
        self.timer_service = timer_service
        self.setWindowTitle("Stage Display")
        self.label_now = QLabel("", self)
        self.label_next = QLabel("", self)
        self.timer_label = QLabel("", self)
        for w in (self.label_now, self.label_next, self.timer_label):
            w.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
            w.setWordWrap(True)
            w.setStyleSheet("color: #DCE7F5; background:#0B121A")
        self.label_now.setFont(QFont("Helvetica", 28))
        self.label_next.setFont(QFont("Helvetica", 22))
        self.timer_label.setFont(QFont("Helvetica", 36))
        lay = QVBoxLayout(self)
        lay.addWidget(self.label_now)
        lay.addWidget(self.label_next)
        lay.addWidget(self.timer_label)
        self.ticker = QTimer(self)
        self.ticker.timeout.connect(self.on_tick)
        self.ticker.start(1000)
        self.hide()

    def set_now_next(self, now_text: str, next_text: str):
        self.label_now.setText(now_text)
        self.label_next.setText(next_text)

    def open_on_screen(self, screen_index: int):
        s = find_screen(QApplication.instance(), screen_index)
        if s:
            g = s.geometry()
            self.setGeometry(g)
            self.showFullScreen()
            self.raise_()

    def close_stage(self):
        self.hide()

    def on_tick(self):
        if self.timer_service.running:
            v = self.timer_service.value()
            mm = v // 60
            ss = v % 60
            self.timer_label.setText(f"{mm:02d}:{ss:02d}")
        else:
            self.timer_label.setText("")