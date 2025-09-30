from flask import Flask, jsonify, request
from werkzeug.serving import make_server

class RemoteServer:
    def __init__(self, song_svc, setlist_svc, projector, timer_svc, port=8765):
        self.song_svc = song_svc
        self.setlist_svc = setlist_svc
        self.projector = projector
        self.timer_svc = timer_svc
        self.port = port
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        app = self.app
        @app.get("/health")
        def health():
            return jsonify({"ok": True})
        @app.get("/songs")
        def songs():
            q = request.args.get("q","")
            return jsonify(self.song_svc.list_songs(q))
        @app.get("/songs/<int:song_id>")
        def song_detail(song_id):
            s = self.song_svc.get_song(song_id)
            return jsonify(s if s else {})
        @app.post("/projector/text")
        def projector_text():
            data = request.get_json(force=True)
            txt = data.get("text","")
            self.projector.set_text(txt)
            return jsonify({"ok": True})
        @app.post("/projector/timer/start")
        def timer_start():
            seconds = int(request.args.get("sec","0"))
            self.timer_svc.start(seconds)
            return jsonify({"ok": True, "seconds": seconds})
        @app.post("/projector/timer/stop")
        def timer_stop():
            self.timer_svc.stop()
            return jsonify({"ok": True})

    def run(self):
        srv = make_server("0.0.0.0", self.port, self.app)
        srv.serve_forever()