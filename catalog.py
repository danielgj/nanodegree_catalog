from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


@app.route('/login')
def showLogin():
    return render_template('login.html')

@app.route('/logout')
def showLogout():
    return "Logout"

@app.route('/')
def showHome():
    return render_template('home.html')

@app.route('/catalog/<string:category>/items/')
def showItems(category):
    return render_template('category_page.html')

@app.route('/catalog/<string:category>/<string:item>')
def showItemDetail(category, item):
    return render_template('item_detail.html')

@app.route('/catalog/items/new')
def newItem():
    return render_template('item_add.html')

@app.route('/catalog/<string:item>/edit')
def editItem(item):
    return render_template('item_edit.html')

@app.route('/catalog/<string:item>/delete')
def deleteItem(item):
    return render_template('item_delete.html')

@app.route('/catalog.json')
def showJSON():
    return "JSON output"

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)