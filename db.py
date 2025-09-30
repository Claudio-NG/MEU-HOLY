import sqlite3
from datetime import datetime

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS songs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        ccli TEXT,
        tags TEXT,
        created_at TEXT,
        updated_at TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS lyrics(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        song_id INTEGER NOT NULL,
        label TEXT,
        order_index INTEGER,
        content TEXT,
        FOREIGN KEY(song_id) REFERENCES songs(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS setlists(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS setlist_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setlist_id INTEGER NOT NULL,
        item_type TEXT NOT NULL,
        ref_id INTEGER NOT NULL,
        order_index INTEGER,
        FOREIGN KEY(setlist_id) REFERENCES setlists(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS themes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        font_family TEXT,
        font_size INTEGER,
        color TEXT,
        stroke_color TEXT,
        stroke_width INTEGER,
        align TEXT,
        valign TEXT,
        bg_type TEXT,
        bg_value TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS media(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        path TEXT NOT NULL,
        kind TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        action TEXT,
        payload TEXT
    );
    """
]

class Database:
    def __init__(self, path):
        self.path = path

    def connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self):
        conn = self.connect()
        cur = conn.cursor()
        for stmt in SCHEMA:
            cur.execute(stmt)
        conn.commit()
        conn.close()

    def now(self):
        return datetime.utcnow().isoformat()