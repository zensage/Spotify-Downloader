from flask import Flask, render_template

app = Flask(__name__, template_folder='../templates')
app.config['SECRET_KEY'] = 'secret'

# Import and initialize routes
from .routes import init_routes
init_routes(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(400)
def bad_request(error):
    return render_template('errors/400.html'), 400

@app.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
