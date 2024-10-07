from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
# import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///invoices_database.db'
db = SQLAlchemy(app)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(200), nullable=False)
    vendor_address = db.Column(db.String(200), nullable=False)
    invoice_number = db.Column(db.String(200), nullable=False)
    invoice_date = db.Column(db.DateTime) #, default=datetime.utcnow)
    invoice_price = db.Column(db.Float(2))
    invoice_currency = db.Column(db.String(10))
    invoice_price_in_USD = db.Column(db.Float(2))
    conversion_exchange_rate = db.Column(db.Float(16))


    def __repr__(self):
        return '<Invoice %r>' % self.id

db.create_all()

import currency_list

print(currency_list.currency_list)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        # print(request.form['invoice_date'])

        if request.form['currency'] != 'USD' :

            currency_conversion_data = requests.get('https://api.currencyfreaks.com/v2.0/rates/latest?apikey=f995675724b34c49ad4de85dc9867075').json()
            # currency_conversion_data = currency_conversion_data.json()
            conversion_factor = float(currency_conversion_data['rates'][request.form['currency']])
            invoice_price_in_USD = float(request.form['invoice_price']) * 1 / conversion_factor

        else:

            conversion_factor = 1
            invoice_price_in_USD = request.form['invoice_price']

        new_invoice = Invoice(
            vendor_name = request.form['vendor_name'],
            vendor_address = request.form['vendor_address'],
            invoice_number = request.form['invoice_number'],
            invoice_date = datetime.strptime(request.form['invoice_date'], '%Y-%m-%d'), #datetime(request.form['invoice_date']),
            invoice_price = request.form['invoice_price'],
            invoice_currency = request.form['currency'],
            invoice_price_in_USD = invoice_price_in_USD,
            conversion_exchange_rate = conversion_factor)
                # request.form['currency']

        # datetime.datetime.strptime(date, '%Y-%m-%d')

        try:
            db.session.add(new_invoice)
            db.session.commit()
            return redirect('/')
        except Exception as error:
            # return 'There was an issue adding your invoice. Exception: '
            return str(error)

    else:
        invoices = Invoice.query.order_by(Invoice.id).all()
        # print(invoices)

        invoices_price_sum = 0

        for invoice in invoices :

            invoices_price_sum += invoice.invoice_price_in_USD

        invoices_price_average = invoices_price_sum / len(invoices)

        return render_template('index.html',
            invoices=invoices,
            invoices_price_sum=invoices_price_sum,
            invoices_price_average=invoices_price_average)


@app.route('/delete/<int:id>')
def delete(id):
    invoice_to_delete = Invoice.query.get_or_404(id)

    try:
        db.session.delete(invoice_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that invoice'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    invoice = Invoice.query.get_or_404(id)

    if request.method == 'POST':
        # invoice.content = request.form['content']

        # print(request.form['invoice_date'])

        if request.form['currency'] != 'USD' :

            currency_conversion_data = requests.get('https://api.currencyfreaks.com/v2.0/rates/latest?apikey=f995675724b34c49ad4de85dc9867075').json()
            # currency_conversion_data = currency_conversion_data.json()
            conversion_factor = float(currency_conversion_data['rates'][request.form['currency']])
            invoice_price_in_USD = float(request.form['invoice_price']) * 1 / conversion_factor

        else:

            conversion_factor = 1
            invoice_price_in_USD = request.form['invoice_price']

        print(request.form['vendor_name'])
        print(request.form['invoice_date'])
        print(datetime.strptime(request.form['invoice_date'], '%Y-%m-%d'))
        print(type(datetime.strptime(request.form['invoice_date'], '%Y-%m-%d')))
        print("Debug5000")

        invoice.vendor_name = request.form['vendor_name']
        invoice.vendor_address = request.form['vendor_address']
        invoice.invoice_number = request.form['invoice_number']
        invoice.invoice_date = datetime.strptime(request.form['invoice_date'], '%Y-%m-%d') #datetime(request.form['invoice_date']),
        invoice.invoice_price = request.form['invoice_price']
        invoice.invoice_currency = request.form['currency']
        invoice.invoice_price_in_USD = invoice_price_in_USD
        invoice.conversion_exchange_rate = conversion_factor
                # request.form['currency']

        # datetime.datetime.strptime(date, '%Y-%m-%d')

        try:
            db.session.commit()
            return redirect('/')
        except Exception as error:
            # return 'There was an issue updating your invoice'
            return str(error)

    else:

        # print(invoice.invoice_date.date())

        return render_template('update.html', invoice=invoice, date_value=invoice.invoice_date.date())

@app.route('/get_sum_with_specific_currency', methods=['POST'])
def get_sum_with_specific_currency():

    currency_conversion_data = requests.get('https://api.currencyfreaks.com/v2.0/rates/latest?apikey=f995675724b34c49ad4de85dc9867075').json()
    conversion_factor = float(currency_conversion_data['rates'][request.form['currency']])    

    invoices = Invoice.query.order_by(Invoice.id).all()
    # print(invoices)

    invoices_price_sum = 0

    for invoice in invoices :

        invoices_price_sum += invoice.invoice_price_in_USD

    invoices_price_average = invoices_price_sum / len(invoices)

    sum_after_conversion = invoices_price_sum * (1 / conversion_factor)

    return render_template('index.html',
            invoices=invoices,
            invoices_price_sum=invoices_price_sum,
            invoices_price_average=invoices_price_average,
            conversion_sentence="Conversion of the sum of all invoice prices at currency " + request.form['currency'] + " = ",
            conversion_value= sum_after_conversion)

@app.route('/get_average_with_specific_currency', methods=['POST'])
def get_average_with_specific_currency():

    currency_conversion_data = requests.get('https://api.currencyfreaks.com/v2.0/rates/latest?apikey=f995675724b34c49ad4de85dc9867075').json()
    conversion_factor = float(currency_conversion_data['rates'][request.form['currency']])    

    invoices = Invoice.query.order_by(Invoice.id).all()
    # print(invoices)

    invoices_price_sum = 0

    for invoice in invoices :

        invoices_price_sum += invoice.invoice_price_in_USD

    invoices_price_average = invoices_price_sum / len(invoices)

    average_after_conversion = invoices_price_average * (1 / conversion_factor)

    return render_template('index.html',
            invoices=invoices,
            invoices_price_sum=invoices_price_sum,
            invoices_price_average=invoices_price_average,
            conversion_sentence="Conversion of the average of all invoice prices at currency " + request.form['currency'] + " = ",
            conversion_value= average_after_conversion)

if __name__ == "__main__":
    app.run(debug=True)
