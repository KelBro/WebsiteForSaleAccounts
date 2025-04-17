from flask import Flask, render_template
from data import db_session
from data.__all_models import catalog_accounts

app = Flask(__name__)
app.config['SECRET_KEY'] = 'o/f#b>v]Twg,pY*3ZrCjRs6EI3AQ/gt.UA!*e2w{f{p74b2?{@W0qFNs–TB.43[>'


@app.route('/')
def index():
    session = db_session.create_session()
    accounts = session.query(catalog_accounts.Catalog).all()
    session.close()
    return render_template('index.html', accounts=accounts)


@app.route('/about')
def about():
    return render_template('about.html')


def main():
    db_session.global_init("db/accounts.db")
    app.run(port=8080, host='127.0.0.1', debug=True)

if __name__ == '__main__':
    main()
