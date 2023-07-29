import sqlite3
import matplotlib.pyplot as plt
import matplotlib
import io
import os.path
import base64
import pandas as pd
from flask import Flask, render_template, request
from sklearn.metrics import r2_score 
from create_db import process_data
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


matplotlib.use('agg')
app = Flask(__name__)


def generate_plot(X=[1, 2, 3, 4], y=[10, 5, 8, 3], xlab='X-axis', ylab='Y-axis', title='Starting plain chart'):
    plt.figure(figsize=(15, 6))
    plt.plot(X, y, color='deepskyblue')
    plt.xlabel(xlab, fontsize=14)
    plt.ylabel(ylab, fontsize=14)
    plt.title(title, fontdict={'fontsize': 20, 'fontname': 'Arial'})
    plt.grid(True)

    return process_plot(plt)

def generate_plot_reg(X, y, xlab='Year', ylab='People living in urban areas [%]'):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    year_pred = pd.DataFrame([y for y in range(int(X.min())-5, int(X.max())+10, 5)])
    values_pred = lr_model.predict(year_pred)
    y_pred = lr_model.predict(X_test)
    r2 = round(r2_score(y_test, y_pred), 2)
    
    plt.figure(figsize=(15, 10))
    plt.subplots_adjust(hspace=1.8)
    plt.subplot(3, 1, 1)
    color = 'royalblue'
    plt.title('Train Data', fontsize=16, color=color)
    plt.scatter(X_train, y_train, color='deepskyblue', label='Actual')
    plt.plot(X_train, lr_model.predict(X_train), color='tomato', label='Predicted')
    plt.xlabel(xlab, fontsize=14, color=color)
    plt.ylabel(ylab, fontsize=14, color=color)
    plt.grid(True)
    plt.legend()

    plt.subplot(3, 1, 2)
    color = 'indigo'
    plt.title('Test Data', fontsize=16, color=color)
    plt.scatter(X_test, y_test, color='deepskyblue', label='Actual')
    plt.plot(X_test, lr_model.predict(X_test), color='tomato', label='Predicted')
    plt.xlabel(xlab, fontsize=14, color=color)
    plt.ylabel(ylab, fontsize=14, color=color)
    plt.grid(True)
    plt.legend()

    plt.subplot(3, 1, 3)
    color = 'dodgerblue'
    plt.title('Prediction', fontsize=16, color=color)
    plt.scatter(X, y, color='deepskyblue', label='Actual')
    plt.plot(year_pred, values_pred, color='gold', linestyle='--', marker='X', label='Predicted')
    plt.xlabel(xlab, fontsize=14, color=color)
    plt.ylabel(ylab, fontsize=14, color=color)
    plt.grid(True)
    plt.legend()

    return process_plot(plt), r2

def process_plot(plt):
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plot_url = base64.b64encode(image_png).decode('utf-8')
    plt.close()
    return plot_url

def select_values(option):
    X, y = return_values(option)
    data_col = process_data(False)
    plot_url = generate_plot(X, y, 'Year', 'People living in urban areas [%]', option)
    return render_template('index.html', plot_url=plot_url, data_col=data_col, title=f'{option} urban areas chart')

def return_values(option):
    conn = sqlite3.connect('local.db')
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info(URBAN)")
    columns_info = cursor.fetchall()
    X = [column[1] for column in columns_info][1:]

    cursor.execute(f'SELECT * FROM URBAN WHERE Region="{option}"')
    values = cursor.fetchall()
    y = values[0][1:]
    return X, y


@app.route('/')
def index():
    create_db = False
    if not os.path.isfile('./local.db'):
        create_db = True
    data_col = process_data(create_db=create_db)
    plot_url = generate_plot()
    desc = 'Matplotlib in Flask'
    return render_template('index.html', plot_url=plot_url, data_col=data_col,  title=desc)

@app.route('/regress', methods=['POST'])
def reg():
    option_value = request.form['regression_value']
    X, y = return_values(option_value)
    X = [int(i) for i in X]
    X = pd.DataFrame(X)
    y = list(y)
    plot_url, r2 = generate_plot_reg(X, y)
    return render_template('reg.html', plot_url=plot_url, title=option_value, r2=r2)

@app.route('/process', methods=['POST'])
def process():
    option_value = request.form['option_value']
    return select_values(option_value)


if __name__ == '__main__':
    app.run(debug=True)
