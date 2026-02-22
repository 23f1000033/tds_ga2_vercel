import json
import numpy as np
from http.server import BaseHTTPRequestHandler

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Expose-Headers": "Access-Control-Allow-Origin",
}

DATA = [
  {"region":"apac","service":"recommendations","latency_ms":196.92,"uptime_pct":97.52,"timestamp":20250301},
  {"region":"apac","service":"analytics","latency_ms":215.23,"uptime_pct":98.142,"timestamp":20250302},
  {"region":"apac","service":"recommendations","latency_ms":178.05,"uptime_pct":99.124,"timestamp":20250303},
  {"region":"apac","service":"checkout","latency_ms":187.17,"uptime_pct":97.967,"timestamp":20250304},
  {"region":"apac","service":"analytics","latency_ms":201.07,"uptime_pct":98.284,"timestamp":20250305},
  {"region":"apac","service":"recommendations","latency_ms":106.28,"uptime_pct":97.326,"timestamp":20250306},
  {"region":"apac","service":"support","latency_ms":210.01,"uptime_pct":97.963,"timestamp":20250307},
  {"region":"apac","service":"catalog","latency_ms":208.43,"uptime_pct":97.15,"timestamp":20250308},
  {"region":"apac","service":"recommendations","latency_ms":180.81,"uptime_pct":99.15,"timestamp":20250309},
  {"region":"apac","service":"recommendations","latency_ms":181.06,"uptime_pct":98.27,"timestamp":20250310},
  {"region":"apac","service":"catalog","latency_ms":110.59,"uptime_pct":97.685,"timestamp":20250311},
  {"region":"apac","service":"checkout","latency_ms":145.25,"uptime_pct":98.555,"timestamp":20250312},
  {"region":"emea","service":"recommendations","latency_ms":207.35,"uptime_pct":98.063,"timestamp":20250301},
  {"region":"emea","service":"support","latency_ms":218.31,"uptime_pct":97.977,"timestamp":20250302},
  {"region":"emea","service":"recommendations","latency_ms":229.28,"uptime_pct":97.288,"timestamp":20250303},
  {"region":"emea","service":"support","latency_ms":185.18,"uptime_pct":98.834,"timestamp":20250304},
  {"region":"emea","service":"support","latency_ms":139.58,"uptime_pct":98.413,"timestamp":20250305},
  {"region":"emea","service":"catalog","latency_ms":130.32,"uptime_pct":97.45,"timestamp":20250306},
  {"region":"emea","service":"checkout","latency_ms":144.9,"uptime_pct":97.865,"timestamp":20250307},
  {"region":"emea","service":"support","latency_ms":144.18,"uptime_pct":97.552,"timestamp":20250308},
  {"region":"emea","service":"support","latency_ms":195.86,"uptime_pct":98.869,"timestamp":20250309},
  {"region":"emea","service":"payments","latency_ms":159.95,"uptime_pct":97.614,"timestamp":20250310},
  {"region":"emea","service":"checkout","latency_ms":216.72,"uptime_pct":98.289,"timestamp":20250311},
  {"region":"emea","service":"catalog","latency_ms":224.75,"uptime_pct":99.003,"timestamp":20250312},
  {"region":"amer","service":"support","latency_ms":136.17,"uptime_pct":97.238,"timestamp":20250301},
  {"region":"amer","service":"support","latency_ms":118.85,"uptime_pct":98.276,"timestamp":20250302},
  {"region":"amer","service":"payments","latency_ms":137.36,"uptime_pct":98.956,"timestamp":20250303},
  {"region":"amer","service":"catalog","latency_ms":168.64,"uptime_pct":98.682,"timestamp":20250304},
  {"region":"amer","service":"recommendations","latency_ms":190.73,"uptime_pct":98.58,"timestamp":20250305},
  {"region":"amer","service":"payments","latency_ms":113.19,"uptime_pct":99.49,"timestamp":20250306},
  {"region":"amer","service":"recommendations","latency_ms":204.79,"uptime_pct":98.8,"timestamp":20250307},
  {"region":"amer","service":"analytics","latency_ms":122.95,"uptime_pct":98.943,"timestamp":20250308},
  {"region":"amer","service":"analytics","latency_ms":143.84,"uptime_pct":98.273,"timestamp":20250309},
  {"region":"amer","service":"checkout","latency_ms":172.84,"uptime_pct":98.882,"timestamp":20250310},
  {"region":"amer","service":"recommendations","latency_ms":129.01,"uptime_pct":98.817,"timestamp":20250311},
  {"region":"amer","service":"analytics","latency_ms":178.29,"uptime_pct":97.92,"timestamp":20250312},
]


class handler(BaseHTTPRequestHandler):

    def send_cors_headers(self):
        for key, value in CORS_HEADERS.items():
            self.send_header(key, value)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            payload = json.loads(body)
        except Exception:
            self.send_response(400)
            self.send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
            return

        regions = payload.get("regions", [])
        threshold_ms = payload.get("threshold_ms", 180)

        result = {}
        for region in regions:
            records = [r for r in DATA if r["region"] == region]
            if not records:
                result[region] = {"error": "No data found"}
                continue
            latencies = [r["latency_ms"] for r in records]
            uptimes = [r["uptime_pct"] for r in records]
            result[region] = {
                "avg_latency": round(float(np.mean(latencies)), 4),
                "p95_latency": round(float(np.percentile(latencies, 95)), 4),
                "avg_uptime": round(float(np.mean(uptimes)), 4),
                "breaches": int(sum(1 for l in latencies if l > threshold_ms)),
            }

        self.send_response(200)
        self.send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
