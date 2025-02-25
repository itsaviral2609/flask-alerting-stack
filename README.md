# Flask Metrics Monitoring with Grafana, Prometheus, Slack, and PagerDuty

## Overview
This project integrates **Flask**, **Prometheus**, **Grafana**, **Slack**, and **PagerDuty** to enable real-time monitoring, alerting, and visualization of metrics. It uses **Prometheus** to scrape application metrics, **Grafana** for visualization, and **Slack/PagerDuty** for alert notifications based on threshold breaches.

---

![Screenshot from 2025-02-25 16-41-21](https://github.com/user-attachments/assets/d8fd18b2-8ae2-4189-8bb6-bdfd18d97abb)


## Features
- **Flask Application Metrics Exposure** (via `/metrics` endpoint)
- **Prometheus Monitoring & Alerting**
- **Grafana Dashboard Visualization**
- **Slack & PagerDuty Alert Integration**
- **Docker-Compose for Easy Deployment**

---

## Project Structure
```

/your-project
│── app.py  # Flask application
│── docker-compose.yml  # Docker Compose File
│── dockerfile  # Flask App container
│── grafana.ini  # Grafana Configuration
│── prometheus/
│    ├── alertmanager/
│    │   ├── alertmanager.yml  # Slack & PagerDuty Alerts
│    │   ├── prometheus.yml  # Prometheus Configuration
│    ├── rules/
│    │   ├── sample.alerts.yml  # Alert Rules
│    ├── targets/
│    │   ├── alert_manager.json  # Alert Manager Targets
│── requirements.txt  # Dependencies
│── README.md  # Documentation

```

---

## Configuration Details

### **1. Flask Application**
The Flask application exposes metrics using `prometheus_client`.

```python
from flask import Flask
from prometheus_client import Counter, generate_latest

app = Flask(__name__)
request_count = Counter('flask_app_requests_total', 'Total requests to the Flask App')

@app.route('/')
def home():
    request_count.inc()
    return "Hello, Flask Monitoring!"

@app.route('/metrics')
def metrics():
    return generate_latest()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

### **2. Prometheus Configuration (prometheus.yml)**
```yaml
global:
  scrape_interval: 15s  # Default scrape interval
  evaluation_interval: 5s

scrape_configs:
  - job_name: 'flask_app'
    scrape_interval: 5s
    metrics_path: '/metrics'
    static_configs:
      - targets: ['flask-app:5000']
  
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['node_exporter:9100']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - 'alertmanager:9093'

rule_files:
 - "rules/*.yml"
```

---

### **3. Load Test for CPU Scraping Metrics**
To simulate high CPU usage and test Prometheus scraping under load, a CPU-intensive computation is executed continuously in a background thread within the Flask app.

You can manually trigger high CPU usage testing using:
```sh
ab -n 1000 -c 10 http://localhost:5000/
```
This command sends 1000 requests with 10 concurrent clients to the Flask app.



### **4. Alertmanager Configuration (alertmanager.yml)**
```yaml
global:
  slack_api_url: 'https://hooks.slack.com/services/TOKEN'
  pagerduty_url: 'https://events.pagerduty.com/generic/TOKEN'

route:
  receiver: 'pagerduty-notifications'
  group_by: ['alertname', 'instance', 'severity']

  routes:
    - receiver: "pagerduty-notifications"
      match_re:
        severity: critical|warning

    - receiver: "slack-notifications"
      match_re:
        severity: critical|warning

receivers:
- name: 'pagerduty-notifications'
  pagerduty_configs:
  - service_key: YOUR_SERVICE_KEY
    send_resolved: true

- name: 'slack-notifications'
  slack_configs:
  - channel: '#alerts'
    send_resolved: true
    title: "[{{ .Status }}] {{ .CommonLabels.alertname }} Alert"
    text: "Alert: {{ .Annotations.description }}"
```

---

### **5. Alert Rules (sample-rules.yml)**
```yaml
groups:
- name: cpu_alerts
  rules:
  - alert: HighCPUUsage
    expr: 100 * (1 - avg by(instance) (rate(process_cpu_seconds_total[1m]))) > 30
    for: 1m
    labels:
      severity: "warning"
    annotations:
      description: "CPU Usage has exceeded 30% threshold"
  
  - alert: CriticalCPUUsage
    expr: 100 * (1 - avg by(instance) (rate(process_cpu_seconds_total[1m]))) > 50
    for: 2m
    labels:
      severity: "critical"
    annotations:
      description: "CPU Usage has exceeded critical 50% threshold"
```

---

### **6. Grafana Configuration (grafana.ini)**
```ini
[security]
admin_user = admin
admin_password = password

[server]
http_port = 3000

[paths]
data = /var/lib/grafana
logs = /var/log/grafana
```

---

### **7. Docker-Compose Configuration (docker-compose.yml)**
```yaml
version: '3.8'

networks:
  flask-monitoring:
    driver: bridge

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    networks:
      - flask-monitoring

  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
    ports:
      - "9093:9093"
    networks:
      - flask-monitoring

  grafana:
    image: grafana/grafana-enterprise:latest
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - ./grafana.ini:/etc/grafana/grafana.ini
    networks:
      - flask-monitoring

  flask-app:
    build: .
    container_name: flask-app
    ports:
      - "5000:5000"
    networks:
      - flask-monitoring
```

---

## Deployment
1. **Clone the Repository**
```sh
git clone https://github.com/your-repo.git && cd your-repo
```
2. **Start the Stack**
```sh
docker-compose up -d --build
```
3. **Verify Services**
```sh
docker ps
```
4. **Access Services**:
   - **Flask App:** `http://localhost:5000`
   - **Prometheus:** `http://localhost:9090`
   - **Alertmanager:** `http://localhost:9093`
   - **Grafana:** `http://localhost:3000`

---

## Use your slack and PagerDuty URL! I have used my own api for project

![Screenshot from 2025-02-13 15-08-13](https://github.com/user-attachments/assets/fa4ec00d-3dea-4684-b1cf-e06f778d73aa)
![Screenshot from 2025-02-14 22-01-45](https://github.com/user-attachments/assets/6654d87d-1b0d-4db8-9590-f9328e0cde2c)
![Screenshot from 2025-02-15 10-26-41](https://github.com/user-attachments/assets/09fe8cec-dd39-4a1b-a783-615f03c5e553)
![Screenshot from 2025-02-25 16-10-33](https://github.com/user-attachments/assets/ca942258-073c-460d-8efd-29b4c6b03770)



## Conclusion
This setup ensures a **full-stack monitoring solution** for Flask applications with **Prometheus, Grafana, Slack, and PagerDuty alerts** for observability and reliability.

