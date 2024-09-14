from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    # Home page with default content
    return render_template('base.html', content_url='/')

@app.route('/cloudbeaver')
def cloudbeaver():
    # Embed CloudBeaver inside an iframe
    return render_template('base.html', content_url='http://localhost:8978')

@app.route('/jupyterlab')
def jupyterlab():
    # Embed JupyterLab inside an iframe
    return render_template('base.html', content_url='http://localhost:8888')

# Add more routes for other components as needed
# e.g., Spark UI, MinIO, etc.

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

