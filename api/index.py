from http.server import BaseHTTPRequestHandler
import json, math, os

data_path = os.path.join(os.path.dirname(__file__), "../data/latency.json")
with open(data_path) as f:
    ALL_RECORDS = json.load(f)

def compute_metrics(records, threshold_ms):
    latencies = [r["latency_ms"] for r in records]
    uptimes   = [r["uptime_pct"] for r in records]
    n = len(latencies)
    sorted_lat = sorted(latencies)
    p95_index  = math.ceil(0.95 * n) - 1
    return {
        "avg_latency": round(sum(latencies) / n, 4),
        "p95_latency": round(sorted_lat[p95_index], 4),
        "avg_uptime":  round(sum(uptimes) / n, 4),
        "breaches":    sum(1 for l in latencies if l > threshold_ms)
    }

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self._cors(200)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        regions = [r.lower() for r in body.get("regions", [])]
        threshold = body.get("threshold_ms", 180)

        result = {}
        for region in regions:
            recs = [r for r in ALL_RECORDS if r["region"] == region]
            if recs:
                result[region] = compute_metrics(recs, threshold)

        self._cors(200)
        self.wfile.write(json.dumps(result).encode())

    def _cors(self, code):
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
