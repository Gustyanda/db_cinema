from email.policy import default
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import uuid, base64

app=Flask(__name__)
db=SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:Kehidupan6@localhost:5432/db_cinema_backup?sslmode=disable'



class Manager(db.Model):
    id=db.Column(db.Integer, primary_key=True, index=True)
    public_id=db.Column(db.String, nullable=False)
    name=db.Column(db.String, nullable=False)
    username=db.Column(db.String, nullable=False, unique=True)
    password=db.Column(db.String, nullable=False, unique=True)
    status=db.Column(db.Boolean)

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True, index=True)
    public_id=db.Column(db.String, nullable=False)
    name=db.Column(db.String, nullable=False)
    username=db.Column(db.String, nullable=False, unique=True)
    password=db.Column(db.String, nullable=False, unique=True)
    balance=db.Column(db.Numeric(15,2), nullable=False, default=0)
    paygate_rel=db.relationship('Paygate', backref='user')
    order_rel=db.relationship('Order', backref='user')
# on progress history

class Category(db.Model):
    id=db.Column(db.Integer, primary_key=True, index=True)
    tag=db.Column(db.String, nullable=False)
    movie_rel=db.relationship('Movie', backref='category')

class Movie(db.Model):
    id=db.Column(db.Integer, primary_key=True, index=True)
    title=db.Column(db.String, nullable=False)
    category_id=db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    schedule_rel=db.relationship('Schedule', backref='movie')

class Theater(db.Model):
    id=db.Column(db.Integer, primary_key=True, index=True)
    name=db.Column(db.String, nullable=False)
    capacity=db.Column(db.Integer, nullable=False)
    schedule_rel=db.relationship('Schedule', backref='theater')

class Schedule(db.Model):
    id=db.Column(db.Integer, primary_key=True, index=True)
    date_show=db.Column(db.Date)
    date_end=db.Column(db.Date)
    status=db.Column(db.String)
    ticket_price=db.Column(db.Numeric(15,2), nullable=False)
    movie_id=db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    theater_id=db.Column(db.Integer, db.ForeignKey('theater.id'), nullable=False)
    order_rel=db.relationship('Order', backref='schedule')

class Paygate(db.Model):
    id=db.Column(db.Integer, primary_key=True, index=True)
    public_id=db.Column(db.String, nullable=False)
    amount=db.Column(db.Numeric(15,2), nullable=False)
    status=db.Column(db.String, default='Top Up')
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))

class Order(db.Model):  
    id=db.Column(db.Integer, primary_key=True, index=True)
    public_id=db.Column(db.String, nullable=False)
    status=db.Column(db.String)
    quantity=db.Column(db.Integer)
    total_price=db.Column(db.Numeric(15,2), nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    schedule_id=db.Column(db.Integer, db.ForeignKey('schedule.id'))
# on hold

# generate database schema on startup, if not exists:
db.create_all()
db.session.commit()



# --------------- Authorization - Manager
def auth_manager(auth):
    encode = base64.b64decode(auth[6:])
    str_encode = encode.decode('ascii')
    lst = str_encode.split(':')
    users = lst[0]
    passes = lst[1]   
    manager = Manager.query.filter_by(username=users).filter_by(password=passes).first()
    if not manager:
        return {
            'message': 'NONE ACCOUNT MANAGER IN DATABASE !' 
        }
    elif manager.status is True:
        return True
    elif not manager.status:
        return False     

def auth_manager_id(auth):
    encode = base64.b64decode(auth[6:])
    str_encode = encode.decode('ascii')
    lst = str_encode.split(':')
    users = lst[0]
    passes = lst[1]   
    manager = Manager.query.filter_by(username=users).filter_by(password=passes).first()
    if manager:
        return str(manager.public_id)
    else:
        return 0

# --------------- Authorization - User
def auth_user(auth):
    encode = base64.b64decode(auth[6:])
    str_encode = encode.decode('ascii')
    lst = str_encode.split(':')
    username = lst[0]
    password = lst[1]   
    user = User.query.filter_by(username=username).filter_by(password=password).first()
    if user:
        return str(user.public_id)
    else:
        return 0



# --------------- Cinema - Home
@app.route('/home', methods=['GET'])
def get_home():
    return {
        'message': 'WELCOME TO I-TIK'
    }



# --------------- Cinema - User # on hold
@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    if len(data['name']) == 0:
        return {
            'message': 'NAME REQUIRED FOR NEW USER !'
        }, 400
    
    if 'username' not in data and 'password' not in data:
        return {
            'message': 'USERNAME AND PASSWORD REQUIRED !'
        }, 400

    user = User(
        public_id=str(uuid.uuid4()),
        name=data['name'],
        username=data['username'],
        password=data['password'],
        balance=0,
    )
    db.session.add(user)
    db.session.commit()
    return {
        'message': 'CREATE USER SUCCESSFULLY !'
    }

@app.route('/user/<id>', methods=['GET'])   # authorization separated by user status id
def get_user(id):
    decode = request.headers.get('Authorization')
    allow = auth_user(decode)
    if allow == id:
        user = User.query.filter_by(public_id=id).first_or_404()
        return jsonify([
            {
                'name':user.name,
                'username':user.username,
                'password':user.password,
                'balance':user.balance
            }
        ])

    else:
        return {
            'message': 'ACCESS DENIED !!'
        }, 400

@app.route('/user/<id>', methods=['PUT'])   # authorization separated by user status id
def update_user(id):
    decode = request.headers.get('Authorization')
    allow = auth_user(decode)
    if allow == id:
        data = request.get_json()
        user = User.query.filter_by(public_id=id).first()
        user.username = data['username']
        user.password = data['password']
        db.session.commit()
        return {
            'message': 'DATA SUCCESSFULLY UPDATE !'
        }, 200

    else:
        return {
            'message': 'ACCESS DENIED !!'
        }, 400



# --------------- Cinema - Manager
@app.route('/manager', methods=['GET'])   # authorization separated by manager status true
def get_manager():
    decode = request.headers.get('Authorization')
    allow = auth_manager(decode)
    if allow == True:
        return jsonify ([
            {
                'uuid':manager.public_id,
                'name':manager.name, 
                'username':manager.username, 
                'password':manager.password
            } for manager in Manager.query.all()
        ]), 200

    else:
        return {
            'message': 'ACCESS DENIED !!'
        }, 400

@app.route('/manager/<id>', methods=['GET'])   # authorization separated by manager status id
def get_manager_id(id):
    decode = request.headers.get('Authorization')
    allow = auth_manager_id(decode)
    if allow == id:
        manager = Manager.query.filter_by(public_id=id).first_or_404()
        return jsonify ([
            {
                'uuid':manager.public_id,
                'name':manager.name, 
                'username':manager.username, 
                'password':manager.password
            } 
        ]), 200

    else:
        return {
            'message': 'ACCESS DENIED !!'
        }, 400

@app.route('/manager', methods=['POST'])   # authorization separated by manager status true
def create_manager():
    decode = request.headers.get('Authorization')
    allow = auth_manager(decode)
    if allow == True:
        data = request.get_json()
        if len(data['name']) == 0:
            return {
                'message': 'NAME REQUIRED !'
            }, 400
        
        manager = Manager(
            public_id=str(uuid.uuid4()),
            name=data['name'],
            username=data['username'],
            password=data['password'],
            status=data['status']
        )
        db.session.add(manager)
        db.session.commit()
        return {
            'message': 'CREATE DATA MANAGER SUCCESSFULLY !'
        }, 200

    else:
        return {
            'message': 'ACCESS DENIED !!'
        }, 400

@app.route('/manager/<id>', methods=['PUT'])   # authorization separated by manager status id 
def update_manager(id):
    decode = request.headers.get('Authorization')
    allow = auth_manager_id(decode)
    if allow == id:    
        data = request.get_json()
        manager = Manager.query.filter_by(public_id=id).first_or_404()
        manager.username = data['username']
        manager.password = data['password']
        manager.status = data['status']
        db.session.commit()
        return {
            'message': 'DATA SUCCESSFULLY UPDATE !'
        }, 200
    
    else:
        return {
            'message': 'ACCESS DENIED !!'
        }, 400

@app.route('/manager/<id>', methods=['DELETE'])   # authorization separated by manager status true, to delete spesific manager id
def delete_manager(id):
    decode = request.headers.get('Authorization')
    allow = auth_manager(decode)
    if allow == True:
        manager = Manager.query.filter_by(public_id=id).first_or_404()
        db.session.delete(manager)
        db.session.commit()
        return {
            'message': 'DATA DELETE SUCCESSFULLY !'
        }, 200

    else:
        return {
            'message': 'ACCESS DENIED !!'
        }, 400



# --------------- Cinema - Category
@app.route('/category', methods=['GET'])   # authorization separated by manager status true
def get_category():
    decode = request.headers.get('Authorization')
    allow = auth_manager(decode)
    if allow == True:
        return jsonify ([
            {
                'tag':category.tag
            } for category in Category.query.all()
        ]), 200
    
    else:
        return {
            'message': 'ACCESS DENIED !!'
        }, 400

@app.route('/category', methods=['POST'])   # authorization separated by manager status true
def create_category():
    decode = request.headers.get('Authorization')
    allow = auth_manager(decode)
    if allow == True:
        data = request.get_json()
        if len(data['tag']) == 0:
            return {
                'message': 'TAG REQUIRED !'
            }, 400
        
        category = Category(
            tag=data['tag']
        )
        db.session.add(category)
        db.session.commit()
        return {
            'message': 'CREATE CATEGORY SUCCESSFULLY !'
        }

    else:
        return {
            'message': 'ACCESS DENIED !!'
        }, 400  



# --------------- Cinema - Movie
@app.route('/movie', methods=['GET'])
def get_movie():
    return jsonify([
        {
            'title': movie.title,
            'category':{
                'id': movie.category.id,
                'tag': movie.category.tag
            }
        } for movie in Movie.query.all()
    ]), 200

@app.route('/movie', methods=['POST'])   # authorization separated by manager status true
def create_movie():
    decode = request.headers.get('Authorization')
    allow = auth_manager(decode)
    if allow == True:
        data = request.get_json()
        if len(data['title']) == 0:
            return {
                'message': 'TITLE REQUIRED !'
            }, 400

        category = Category.query.filter_by(tag=data['tag']).first()
        if not category:
            return {
                'message': 'TAG REQUIRED !'
            }, 400
        
        movie = Movie(
            title=data['title'],
            category_id=category.id
        )
        db.session.add(movie)
        db.session.commit()
        return {
            'message': 'ADDING MOVIE TO LIST SUCCESSFULLY !'
        }

    else:
        return {
            'message': 'ACCESS DENIED !!'
        }, 400 

@app.route('/movie/<title>', methods=['DELETE'])   # authorization separated by manager status true, delete by title
def delete_movie(title):
    decode = request.headers.get('Authorization')
    allow = auth_manager(decode)
    if allow == True:
        movie = Movie.query.filter_by(title=title).first()
        db.session.delete(movie)
        db.session.commit()
        return {
            'message': 'DATA DELETE SUCCESSFULLY !'
        }, 200

    else:
        return {
            'message': 'ACCESS DENIED !!'
        }, 400



# --------------- Cinema - Theater
@app.route('/theater', methods=['GET'])
def get_theater():
    return jsonify([
        {
            'name':theater.name,
            'capacity':theater.capacity
        } for theater in Theater.query.all()
    ]), 200

@app.route('/theater', methods=['POST'])   # authorization separated by manager status true
def create_theater():
    decode = request.headers.get('Authorization')
    allow = auth_manager(decode)
    if allow == True:
        data = request.get_json()
        if len(data['name']) == 0:
            return {
                'message': 'NAME THEATER REQUIRD FOR DATA !'
            }, 400

        if not 'capacity' in data:
            return {
                'message': 'CAPACITY REQUIRED !'
            }, 400

        theater = Theater(
            name=data['name'],
            capacity=data['capacity']
        )
        db.session.add(theater)
        db.session.commit()
        return {
            'message': 'DATA THEATER SUCCESSFULLY CREATE !'
        }, 200

    else:
        return {
            'message': 'ACCESS DENIED !!'
        }, 400 

@app.route('/theater/<name>', methods=['PUT'])   # authorization separated by manager status true, update by name
def update_theater(name):
    decode = request.headers.get('Authorization')
    allow = auth_manager(decode)
    if allow == True:
        data = request.get_json()
        theater = Theater.query.filter_by(name=name).first_or_404()
        theater.capacity = data['capacity']
        db.session.commit()
        return {
            'message': 'DATA SUCCESSFULLY UPDATE !'
        }

    else:
        return {
            'message': 'ACCESS DENIED !!'
        }, 400    

@app.route('/theater/<name>', methods=['DELETE'])   # authorization separated by manager status true, name
def delete_theater(name):
    decode = request.headers.get('Authorization')
    allow = auth_manager(decode)
    if allow == True:
        theater = Theater.query.filter_by(name=name).first()
        db.session.delete(theater)
        db.session.commit()
        return {
            'message': 'DATA THEATER SUCCESSFULLY DELETE !'
        }, 200

    else:
        return {
            'message': 'ACCESS DENIED !!'
        }, 400



# --------------- Cinema - Paygate
@app.route('/paygate/<id>', methods=['GET'])   # authorization separated by user status id
def get_top_up(id):
    decode = request.headers.get('Authorization')
    allow = auth_user(decode)
    if allow == id:
        user = User.query.filter_by(public_id=id).first_or_404()
        return jsonify([
            {
                'amount':paygate.amount,
                'status':paygate.status,
                'public_id':paygate.public_id,
                'user':{
                    'name':paygate.user.name
                }
            } for paygate in Paygate.query.filter_by(user_id=user.id).all()
        ]), 200


    else:
        return {
            'message': 'ACCESS DENIED !!'
        }, 400

@app.route('/paygate/<id>', methods=['POST'])   # authorization separated by user status id
def top_up(id):
    decode = request.headers.get('Authorization')
    allow = auth_user(decode)
    if allow == id:
        data = request.get_json()
        if (data['amount']) < 25000:
            return {
                'message': 'MINIMUM TOP UP 25.000 !'
            }, 400
        user = User.query.filter_by(public_id=id).first()
        paygate = Paygate(
            public_id=str(uuid.uuid4()),
            amount=data['amount'],
            status='TOP UP',
            user_id=user.id
        )
        user.balance += paygate.amount
        db.session.add(paygate)
        db.session.commit()
        return {
            'message': 'TOP UP SUCCESSFULLY !'
        }, 200

    else:
        return {
            'message': 'ACCESS DENIED !!'
        }, 400    



# --------------- Cinema - Schedule
@app.route('/schedule', methods=['GET'])
def get_schedule():
    schedule =  Schedule.query.filter_by(status='Available').all()
    if schedule:
        return jsonify([
        {
            'date_show': x.date_show,
            'date_end': x.date_end,
            'ticket_price': x.ticket_price,
            'movie':{
                'title': x.movie.title},
            'theater':{
                'name': x.theater.name}
        } for x in schedule
        ]), 200 

    else:
        return {
            'message': 'COMING SOON!'
        }, 400

@app.route('/schedule', methods=['POST'])   # authorization separated by manager status true
def create_schedule():
    decode = request.headers.get('Authorization')
    allow = auth_manager(decode)
    if allow == True:
        data = request.get_json()
        movie = Movie.query.filter_by(title=data['title']).first()
        if not movie:
            return {
                'message': 'MOVIE TITLE REQUIRED !'
            }

        theater = Theater.query.filter_by(name=data['name']).first()
        if not theater:
            return {
                'message': 'THEATER NAME FOR PREMIER SHOW REQUIRED !'
            }

        schedule = Schedule(
            date_show=data['date_show'],
            date_end=data['date_end'],
            status='Unavailable',
            ticket_price=data['ticket_price'],
            movie_id=movie.id,
            theater_id=theater.id
        )
        db.session.add(schedule)
        db.session.commit()
        return {
            'message': 'SCHEDULE PREMIER MOVIE HAS BEEN CREATE !'
        }

    else:
        return {
            'message': 'ACCESS DENIED !!'
        }, 400  

@app.route('/schedule/<id>', methods=['PUT'])   # authorization separated by manager status true
def update_schedule(id):
    decode = request.headers.get('Authorization')
    allow = auth_manager(decode)
    if allow == True:
        data = request.get_json()
        schedule = Schedule.query.filter_by(id=id).first_or_404()  
        schedule.date_show = data['date_show']
        schedule.date_end = data['date_end']
        schedule.status = data['status']
        schedule.ticket_price = data['ticket_price']
        schedule.movie.title = data['title']
        schedule.theater.name = data['name']
        db.session.commit()
        return {
            'message': 'DATA SUCCESSFULLY UPDATE !'
        }

    else:
        return {
            'message': 'ACCESS DENIED !!'
        }, 400   





