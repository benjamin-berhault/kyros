from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    services = [
        {"name": "Kafka", "url": "http://localhost:9092"},
        {"name": "Kafka (Controller)", "url": "http://localhost:29092"},
        {"name": "JupyterLab", "url": "http://localhost:8888"},
        {"name": "Spark Master", "url": "http://localhost:8080"},
        {"name": "Spark Worker 1", "url": "http://localhost:8081"},
        {"name": "Spark Worker 2", "url": "http://localhost:8082"},
    ]
    return render_template('index.html', services=services)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
