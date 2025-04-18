from flask import Flask, render_template
from config_reader import config
from website.data import db_session
from website.data.__all_models import catalog_accounts

app = Flask(__name__)
app.config['SECRET_KEY'] = config.secret_key.get_secret_value()


@app.route('/')
def index():
    try:
        session = db_session.create_session()
        accounts = session.query(catalog_accounts.Catalog).all()
        return render_template('index.html', accounts=accounts)
    except Exception as e:
        print(f"Database error: {e}")
        return render_template('error.html', error="Database error")
    finally:
        if 'session' in locals():
            session.close()

@app.route('/about')
def about():
    return render_template('about.html')

def run_website():
    app.run(port=8080, host='127.0.0.1', debug=False, use_reloader=False)