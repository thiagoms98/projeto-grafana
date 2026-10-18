from time import perf_counter

from flask import Flask, jsonify, render_template_string, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = Flask(__name__)

HTTP_REQUESTS = Counter(
    "webapp_http_requests_total",
    "Total de requisições HTTP da aplicação",
    ["method", "route", "status"],
)
HTTP_DURATION = Histogram(
    "webapp_http_request_duration_seconds",
    "Duração das requisições HTTP em segundos",
    ["route"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)
VISITS = Counter("webapp_visits_total", "Visitas registradas pelo botão da página")

PAGE = """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>App Services | Grafana</title>
  <style>
    *{box-sizing:border-box}body{margin:0;background:#0b1020;color:#e5e7eb;font:16px system-ui,Segoe UI,sans-serif}
    main{max-width:900px;margin:10vh auto;padding:24px}.tag{color:#22d3ee;font-size:13px;font-weight:700;letter-spacing:.12em;text-transform:uppercase}
    h1{font-size:clamp(32px,6vw,54px);margin:12px 0}p{color:#aab4c8;line-height:1.7}.card{margin-top:28px;padding:24px;border:1px solid #29334a;border-radius:16px;background:#121a2c}
    button{border:0;border-radius:8px;background:#6366f1;color:white;padding:12px 18px;font-size:15px;font-weight:700;cursor:pointer}button:hover{background:#818cf8}
    #result{margin-left:12px;color:#67e8f9}.links{display:flex;gap:18px;margin-top:22px}.links a{color:#a5b4fc;text-decoration:none}.status{color:#4ade80}
  </style>
</head>
<body><main>
  <div class="tag">Aplicação monitorada</div><h1>App Services</h1>
  <p>Uma aplicação web simples com métricas de acesso, latência e disponibilidade coletadas pelo Prometheus e exibidas no Grafana.</p>
  <section class="card"><strong>Serviço: <span class="status">online</span></strong><p>Clique para registrar uma visita e gerar atividade para o painel.</p>
    <button id="visit">Registrar visita</button><span id="result" aria-live="polite"></span></section>
  <nav class="links"><a href="/health">Health check</a><a href="/metrics">Métricas Prometheus</a><a href="http://localhost:3000">Grafana</a></nav>
</main><script>
document.querySelector('#visit').addEventListener('click',async()=>{const r=await fetch('/api/visit',{method:'POST'});const d=await r.json();document.querySelector('#result').textContent=`Visitas registradas: ${d.visits}`;});
</script></body></html>"""


@app.before_request
def start_timer():
    request.started_at = perf_counter()


@app.after_request
def record_request(response):
    if request.path != "/metrics":
        route = request.url_rule.rule if request.url_rule else "unmatched"
        HTTP_REQUESTS.labels(request.method, route, str(response.status_code)).inc()
        HTTP_DURATION.labels(route).observe(perf_counter() - request.started_at)
    return response


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.post("/api/visit")
def visit():
    VISITS.inc()
    return jsonify(visits=int(VISITS._value.get()))


@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
