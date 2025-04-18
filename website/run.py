from flask import Flask, render_template, abort
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


@app.route('/account/info/<id_product>')
def account_info(id_product):
    session = db_session.create_session()
    account = session.query(catalog_accounts.Catalog).filter_by(id=id_product).first()
    session.close()

    if not account:
        abort(404)  # Если аккаунт не найден

    return render_template('account_info.html', account=account)


@app.route('/cart')
def cart():
    # Здесь должна быть логика получения товаров в корзине
    return render_template('cart.html', cart_items=[], total_price=0)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/faq')
def faq():
    return render_template('faq.html')


def run_website():
    app.run(port=8080, host='127.0.0.1', debug=False, use_reloader=False)
