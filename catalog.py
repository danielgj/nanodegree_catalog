from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify,
    url_for,
    flash,
    session as login_session,
    make_response)
from sqlalchemy import (
    create_engine,
    asc,
    desc)
from sqlalchemy.orm import sessionmaker
from database_setup import (
    Base,
    Category,
    Item,
    User)
from oauth2client.client import (
    flow_from_clientsecrets,
    FlowExchangeError)
import httplib2
import json
import requests
import random
import string
from functools import wraps


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secret_google.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogapp.db',
                        connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash('You are not allowed to access there')
            return redirect('/login')
    return decorated_function


@app.route('/catalog/json')
def showCatalogJSON():
    categories = session.query(Category).all()
    new_cats = []
    for cat in categories:
        items_for_cat = session.query(Item).filter_by(category=cat).all()
        serialized_cat = {}
        serialized_cat['id'] = cat.id
        serialized_cat['name'] = cat.name
        if len(items_for_cat) != 0:
            serialized_cat['Item'] = [i.serialize for i in items_for_cat]
        new_cats.append(serialized_cat)
    return jsonify(Category=new_cats)


@app.route('/catalog/<string:category>/json')
def showCategoryItemsJSON(category):
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(name=category).one()
    category_items = session.query(Item).filter_by(category=category).all()

    new_cat = {
        'id': category.id,
        'name': category.name,
        'Item': []
    }
    if len(category_items) != 0:
        new_cat['Item'] = [i.serialize for i in category_items]

    return jsonify(new_cat)


@app.route('/catalog/<string:category>/<string:item>/json')
def showItemDetailJSON(category, item):
    cSelected = session.query(Category).filter_by(name=category).one()
    iSelected = session.query(Item).filter_by(
        category=cSelected,
        title=item
        ).one()
    item = {
        'category': cSelected.name,
        'title': iSelected.title,
        'description': iSelected.description
    }
    return jsonify(item)


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/')
def showHome():
    categories = session.query(Category).order_by(asc(Category.name))
    latest_items = session.query(Item).order_by(desc(Item.id)).limit(10)
    return render_template(
        'home.html',
        categories=categories,
        items=latest_items)


@app.route('/catalog/<string:category>/items/')
def showItems(category):
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(name=category).one()
    category_items = session.query(Item).filter_by(category=category).all()

    return render_template(
        'category_page.html',
        categories=categories,
        items=category_items,
        selected_category=category)


@app.route('/catalog/<string:category>/<string:item>')
def showItemDetail(category, item):
    cSelected = session.query(Category).filter_by(name=category).one()
    iSelected = session.query(Item).filter_by(
        category=cSelected,
        title=item
        ).one()

    return render_template('item_detail.html', item=iSelected)


@app.route('/catalog/items/new', methods=['GET', 'POST'])
@login_required
def newItem():
    if request.method == 'POST':
        newItem = Item(
            title=request.form['title'],
            description=request.form['description'],
            category_id=request.form['category'],
            user_id=login_session['user_id'])
        session.add(newItem)
        flash('New item %s Successfully Created' % newItem.title)
        session.commit()
        return redirect(url_for('showHome'))
    else:
        categories = session.query(Category).order_by(asc(Category.name))
        return render_template('item_add.html', categories=categories)


@app.route('/catalog/<string:item>/edit', methods=['GET', 'POST'])
@login_required
def editItem(item):
    item_selected = session.query(Item).filter_by(title=item).one()
    if request.method == 'POST':
        item_selected.title = request.form['title']
        item_selected.description = request.form['description']
        item_selected.category_id = request.form['category']
        session.commit()
        flash('%s successfully edited' % item_selected.title)
        return redirect(url_for('showHome'))
    else:
        if(item_selected.user_id != login_session['user_id']):
            flash(
                'You do not have permission to edit %s' %
                item_selected.title)
            return redirect(url_for('showHome'))
        else:
            categories = session.query(Category).order_by(asc(Category.name))
            return render_template(
                'item_edit.html',
                categories=categories,
                item=item_selected)


@app.route('/catalog/<string:item>/delete', methods=['GET', 'POST'])
@login_required
def deleteItem(item):
    item_selected = session.query(Item).filter_by(title=item).one()
    if request.method == 'POST':
        session.delete(item_selected)
        session.commit()
        flash('%s successfully deleted' % item_selected.title)
        return redirect(url_for('showHome'))
    else:
        if(item_selected.user_id != login_session['user_id']):
            flash('You do not have permission to delete %s' % newItem.title)
            return redirect(url_for('showHome'))
        else:
            return render_template('item_delete.html', item=item_selected)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if 'state' in login_session and request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            'client_secret_google.json',
            scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')

    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # Check if user exists in DB
    user_id = getUserID(data['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        print Exception
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/disconnect')
def disconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's session.
        del login_session['user_id']
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        flash("You have successfully been logged out.")
        return redirect(url_for('showHome'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
