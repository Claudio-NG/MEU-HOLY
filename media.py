import os
from pathlib import Path

AUDIO_EXT = (".mp3", ".wav", ".aac", ".m4a", ".ogg", ".flac")
VIDEO_EXT = (".mp4", ".mov", ".mkv", ".avi", ".webm")
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp", ".bmp")

class MediaService:
    def __init__(self):
        self.audio_dir = ""
        self.video_dir = ""
        self.image_dir = ""

    def set_dirs(self, audio_dir: str, video_dir: str, image_dir: str):
        self.audio_dir = audio_dir or ""
        self.video_dir = video_dir or ""
        self.image_dir = image_dir or ""

    def classify(self, path: str) -> str:
        p = path.lower()
        if p.endswith(IMAGE_EXT):
            return "image"
        if p.endswith(VIDEO_EXT):
            return "video"
        if p.endswith(AUDIO_EXT):
            return "audio"
        return "other"

    def _scan_dir(self, d: str, exts) -> list:
        if not d or not os.path.isdir(d):
            return []
        out = []
        for root, _, files in os.walk(d):
            for f in files:
                if f.lower().endswith(exts):
                    out.append(str(Path(root) / f))
        out.sort()
        return out

    def list_audio(self) -> list:
        return self._scan_dir(self.audio_dir, AUDIO_EXT)

    def list_video(self) -> list:
        return self._scan_dir(self.video_dir, VIDEO_EXT)

    def list_images(self) -> list:
        return self._scan_dir(self.image_dir, IMAGE_EXT)