from typing import List, Optional, Dict, Any
from db import Database

class SongService:
    def __init__(self, db: Database):
        self.db = db

    def create_song(self, title: str, author: str = "", ccli: str = "", tags: str = "") -> int:
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO songs(title, author, ccli, tags, created_at, updated_at) VALUES(?,?,?,?,?,?)", (title, author, ccli, tags, self.db.now(), self.db.now()))
        song_id = cur.lastrowid
        conn.commit()
        conn.close()
        return song_id

    def upsert_lyric_blocks(self, song_id: int, blocks: List[Dict[str, Any]]):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM lyrics WHERE song_id=?", (song_id,))
        for i, b in enumerate(blocks):
            cur.execute("INSERT INTO lyrics(song_id, label, order_index, content) VALUES(?,?,?,?)", (song_id, b.get("label",""), i, b.get("content","")))
        conn.commit()
        conn.close()

    def list_songs(self, q: str = "") -> List[Dict[str, Any]]:
        conn = self.db.connect()
        cur = conn.cursor()
        if q:
            cur.execute("SELECT * FROM songs WHERE title LIKE ? OR tags LIKE ? ORDER BY title", (f"%{q}%", f"%{q}%"))
        else:
            cur.execute("SELECT * FROM songs ORDER BY title")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def get_song(self, song_id: int) -> Optional[Dict[str, Any]]:
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM songs WHERE id=?", (song_id,))
        s = cur.fetchone()
        if not s:
            conn.close()
            return None
        cur.execute("SELECT * FROM lyrics WHERE song_id=? ORDER BY order_index", (song_id,))
        blocks = [dict(r) for r in cur.fetchall()]
        conn.close()
        d = dict(s)
        d["blocks"] = blocks
        return d

class SetlistService:
    def __init__(self, db: Database):
        self.db = db

    def create_setlist(self, name: str) -> int:
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO setlists(name, created_at) VALUES(?,?)", (name, self.db.now()))
        setlist_id = cur.lastrowid
        conn.commit()
        conn.close()
        return setlist_id

    def add_song_item(self, setlist_id: int, song_id: int, order_index: int):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO setlist_items(setlist_id, item_type, ref_id, order_index) VALUES(?,?,?,?)", (setlist_id, "song", song_id, order_index))
        conn.commit()
        conn.close()

    def get_setlist(self, setlist_id: int) -> Dict[str, Any]:
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM setlists WHERE id=?", (setlist_id,))
        s = cur.fetchone()
        cur.execute("SELECT * FROM setlist_items WHERE setlist_id=? ORDER BY order_index", (setlist_id,))
        items = [dict(r) for r in cur.fetchall()]
        conn.close()
        return {"id": s["id"], "name": s["name"], "items": items}

    def list_setlists(self) -> List[Dict[str, Any]]:
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM setlists ORDER BY created_at DESC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

class ThemeService:
    def __init__(self, db: Database):
        self.db = db

    def list_themes(self) -> List[Dict[str, Any]]:
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM themes ORDER BY name")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def create_theme(self, name: str, font_family: str, font_size: int, color: str, stroke_color: str, stroke_width: int, align: str, valign: str, bg_type: str, bg_value: str) -> int:
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO themes(name, font_family, font_size, color, stroke_color, stroke_width, align, valign, bg_type, bg_value) VALUES(?,?,?,?,?,?,?,?,?,?)", (name, font_family, font_size, color, stroke_color, stroke_width, align, valign, bg_type, bg_value))
        theme_id = cur.lastrowid
        conn.commit()
        conn.close()
        return theme_id

    def get_theme(self, theme_id: int) -> Optional[Dict[str, Any]]:
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM themes WHERE id=?", (theme_id,))
        r = cur.fetchone()
        conn.close()
        return dict(r) if r else None

class TimerService:
    def __init__(self):
        self.seconds = 0
        self.running = False

    def start(self, seconds: int):
        self.seconds = max(0, seconds)
        self.running = True

    def tick(self):
        if self.running and self.seconds > 0:
            self.seconds -= 1
        if self.seconds == 0:
            self.running = False

    def stop(self):
        self.running = False

    def value(self) -> int:
        return self.seconds