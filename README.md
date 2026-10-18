# App Services — Grafana

Aplicação web simples com monitoramento local usando Prometheus e Grafana.

## Iniciar

Com Docker Desktop aberto, execute na pasta do projeto:

```powershell
docker compose up --build -d
```

| Serviço | Endereço |
|---|---|
| Aplicação web | http://localhost:8000 |
| Health check | http://localhost:8000/health |
| Métricas Prometheus | http://localhost:8000/metrics |
| Prometheus | http://localhost:9090/targets |
| Grafana | http://localhost:3000 |

Grafana: usuário `admin`, senha `admin`. O datasource Prometheus e o painel **App Services · Monitoramento** são carregados automaticamente.

## Evidências

- `http://localhost:8000/health` retorna `{"status":"ok"}`.
- `http://localhost:8000/metrics` mostra contadores HTTP, duração das requisições e visitas.
- `http://localhost:9090/targets` mostra o alvo `app-services` como **UP**.
- O painel Grafana apresenta disponibilidade, taxa de requisições, latência p95, visitas e tráfego por rota.
- Clique em **Registrar visita** na aplicação para gerar dados para os gráficos.

As configurações do painel estão em `grafana/dashboards/app-services.json`; datasource e provisionamento ficam em `grafana/provisioning/`.

## Encerrar

```powershell
docker compose down
```
