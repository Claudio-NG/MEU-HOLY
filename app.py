import sys
import json
import threading
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from db import Database
from services import SongService, SetlistService, ThemeService, TimerService
from projector import ProjectorWindow, StageDisplayWindow
from remote import RemoteServer
from media import MediaService
from main_window import MainWindow

def ensure_root():
    base = Path(__file__).resolve().parent
    return base

def load_config(base: Path):
    cfg_path = base / "config.json"
    if not cfg_path.exists():
        cfg = {
            "projector_screen_index": 0,
            "stage_screen_index": 0,
            "active_theme_id": None,
            "server_port": 8765,
            "audio_dir": "",
            "video_dir": "",
            "image_dir": ""
        }
        cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return json.loads(cfg_path.read_text(encoding="utf-8"))

def save_config(base: Path, cfg: dict):
    (base / "config.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

def ensure_default_themes(theme_svc):
    from themes import DEFAULT_THEMES
    if not theme_svc.list_themes():
        for t in DEFAULT_THEMES:
            theme_svc.create_theme(t["name"], t["font_family"], t["font_size"], t["color"], t["stroke_color"], t["stroke_width"], t["align"], t["valign"], t["bg_type"], t["bg_value"])

def main():
    base = ensure_root()
    cfg = load_config(base)
    db_path = base / "app.db"
    db = Database(str(db_path))
    db.init_schema()
    song_svc = SongService(db)
    setlist_svc = SetlistService(db)
    theme_svc = ThemeService(db)
    timer_svc = TimerService()
    media_svc = MediaService()
    media_svc.set_dirs(cfg.get("audio_dir", ""), cfg.get("video_dir", ""), cfg.get("image_dir", ""))
    app = QApplication(sys.argv)
    projector = ProjectorWindow(theme_svc, timer_svc, media_svc)
    stage = StageDisplayWindow(timer_svc)
    ensure_default_themes(theme_svc)
    themes = theme_svc.list_themes()
    if themes:
        active_id = cfg.get("active_theme_id") or themes[0]["id"]
        t = theme_svc.get_theme(active_id)
        if t:
            projector.apply_theme(t)
            cfg["active_theme_id"] = active_id
            save_config(base, cfg)
    remote = RemoteServer(song_svc, setlist_svc, projector, timer_svc, port=cfg.get("server_port", 8765))
    t = threading.Thread(target=remote.run, daemon=True)
    t.start()
    win = MainWindow(song_svc, setlist_svc, theme_svc, projector, stage, timer_svc, media_svc, base_cfg=(base, cfg, save_config))
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()