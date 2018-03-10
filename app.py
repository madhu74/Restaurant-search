from flask import Flask,flash, redirect, render_template, request, session, abort
from flask import url_for,Response
import os
# import request
from sqlalchemy.exc import IntegrityError
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_, and_
from flask_mongoengine import MongoEngine
# from elasticsearch import Elasticsearch
from flask_elasticsearch import FlaskElasticsearch
from elasticsearch_dsl import Search
from flask import jsonify
import json

# DB model for storing the user information.
from model.user import User, db_session

app = Flask(__name__)
app._static_folder = "/bootstrap/"
app.config['SECRET_KEY'] = 'secretkeyformyapp'

## Setting up mondo connection requirement
mongo_connection_info = os.environ.get('MONGODB_URI')
conn_vals = str(mongo_connection_info).split("//")
sub_str_conn = conn_vals[1].split(":")
mongo_user_name = str(sub_str_conn[0])
mongo_passwrd = str(sub_str_conn[1].split("@")[0])
mongo_host = sub_str_conn[1].split("@")[1]
mongo_port = int(sub_str_conn[-1].split("/")[0])
mongo_db = str(sub_str_conn[-1].split("/")[1])

app.config['MONGODB_SETTINGS'] = {
    'db': mongo_db,
    'host': mongo_host,
    'port': mongo_port,
    'username':mongo_user_name,
    'password': mongo_passwrd
}

# app.config['MONGODB_SETTINGS'] = {
#     'db': 'project',
#     'host': 'mongodb://localhost/project.restaurants'
# }

app.config['ELASTICSEARCH_HOST'] ='localhost:9200'
app.config['ELASTICSEARCH_HTTP_AUTH']= None

es = FlaskElasticsearch()
## Elastic_Search Handle
es.init_app(app)
## Mongo DB handle
db_mondo = MongoEngine(app)


class Restaurants(db_mondo.DynamicDocument):
    """ORM Database using MongoDb, to store Restaurent info."""
    meta = {'collection': 'restaurants'}
    address = db_mondo.DictField()
    borough= db_mondo.StringField(max_length=200)
    cuisine = db_mondo.StringField(max_length=200)
    grades = db_mondo.ListField(db_mondo.DynamicDocument())
    name = db_mondo.StringField(max_length=200)
    restaurant_id = db_mondo.StringField(max_length=15)

search_es_obj = Search(using=es, index='project', doc_type='restaurant')


def login_required(f):
    """Wrapper function for login check"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in", None):
            return redirect(url_for('home'))
        return f(*args, **kwargs)

    ## end login_required
    return decorated_function


@app.route('/')
def home():
    """Home Page"""
    if session.get('logged_in'):
        return redirect(url_for('search'))
    return render_template('login.html')


@app.route('/search', methods=['GET'])
@login_required
def search():
    """Search function to enter the name of the city."""
    if session.get("search_error_message"):
        message = session.get("search_error_message")
        del session["search_error_message"]
        return render_template("search.html",value = message)
    else:
        return render_template("search.html")


@app.route('/process_search', methods=['POST'])
def process_search():
    """Validates the search string and sends it to results"""
    if request.form:
        search_string = request.form.get('search_entry')
        search_string = str(search_string)
        if search_string.isalpha():
            search_string.title()
            return redirect(url_for('view_results',city=search_string, page=1))
        else:
            session['search_error_message'] = "Accepting only Alphabets no special charecters"
            return redirect(url_for('search'))

@app.route('/login', methods=['POST','GET'])
def do_login():
    """Queries the database and validated the user."""
    if request.form:
        if len(request.form['password']) > 0 and len(request.form['password']) <=25 and len(request.form['username']) > 0 and len(request.form['username']) <=25:
            qry_data = db_session.query(User).filter(or_(User.user_name==request.form['username'],User.email_address==request.form['username'])).first()
            if qry_data and check_password_hash(qry_data.password, request.form['password']):
                session['logged_in'] = True
                return redirect(url_for('search'))
        else:
            session['login_error'] = True

    return redirect(url_for('home'))


@app.route("/logout")
def logout():
    """Logs out the system"""
    if session.get('logged_in'):
        session['logged_in'] = False
    return redirect(url_for('home'))


@app.route("/register", methods=['POST','GET'])
def register():
    """ Portal for registeration."""
    if session.get('logged_in'):
        return redirect(url_for('search'))
    elif session.get('error_message'):
        message = session['error_message']
        del session['error_message']
        return render_template("register.html", value=message)
    else:
        return render_template("register.html")


@app.route('/complete_registeration',  methods=['POST'])
def process_register():
    """User details are processed here."""
    if len(request.form['first_name'])<=0 or len(request.form['last_name'])<=0:
        session['error_message'] = "Enter the First Name and Last Name"
        return redirect(url_for('register'))
    if (len(request.form['password'])< 6 and len(request.form['password'])>25) or (len(request.form['username'])<6 and len(request.form['password'])>25):
        session['error_message'] = "The length of the username and password should be between 6 and 25"
        return redirect(url_for('register'))
    else:
        try:
            new_user = User(first_name=request.form['first_name'], last_name=request.form['last_name'], password =generate_password_hash(request.form['password']),
            email_address=request.form['email'],user_name = request.form['username'])
            db_session.add(new_user)
            db_session.commit()
            session['status_message'] = "Successfull Registered"
        except IntegrityError:
            session['error_message'] = 'e-mail address already exist use a new email address'
            db_session.rollback()
            return redirect(url_for('register'))
        except:
            session['error_message'] = 'Fill all the required fields'
            db_session.rollback()
            return redirect(url_for('register'))
    ## end process_register
    return redirect(url_for('home'))


@app.route('/results/<string:city>/<int:page>', methods=['GET'])
@login_required
def view_results(city, page=1):
    """Paginating the Query String."""
    lst = []
    ## cannot find way to send make the elastic search functional
    ## this search query is executed "page" number of time to pagination
    search_es_obj.query("match", borough=city)
    for hit in search_es_obj:
        lst.append(hit.mongo_reference)

    if len(lst)>0:
        ## querying mongo DB ORM
        paginated_restaurents = Restaurants.objects(id__in=lst).paginate(page=page, per_page=5)
        return render_template('results.html', city=city, paginated_restaurents=paginated_restaurents)
    else:
        ## inf no hit in ES the returns back to searcjh
        ## end view_results
        return(url_for('search'))

@app.route('/restaurants/<string:name>',methods=['GET'])
@login_required
def restaurant_info(name):
    result = json.loads(Restaurants.objects.get(name=name).to_json())
    return render_template('restaurant.html',restaurant=result)

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True, port=5000)
