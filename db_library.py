from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid, base64, requests
app = Flask(__name__)
db = SQLAlchemy(app)

# # config
app.config['SECRET KEY']='secret'
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:Kehidupan6@localhost:5432/db_alchemy_book2?sslmode=disable'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True




author_book = db.Table('author_book',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), nullable=False),
    db.Column('author_id', db.Integer, db.ForeignKey('author.id'), nullable=False))

# # class
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    tag = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(50), nullable=False)
    public_id = db.Column(db.String, nullable=False)
    books = db.relationship('Book', backref='kategori', lazy='dynamic')

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    title = db.Column(db.String(30), nullable=False)
    release = db.Column(db.Date, nullable=False)
    public_id = db.Column(db.String, nullable=False)
    categories_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    quantity = db.Column(db.Integer)
    categories = db.relationship('Category', backref='buku')
    auth_book = db.relationship('Author', backref='buku', secondary='author_book')
    rents = db.relationship('Rent', backref='buku')

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(30), nullable=False)
    bod = db.Column(db.Date, nullable=False)
    public_id = db.Column(db.String, nullable=False)
    auth_author = db.relationship('Book', backref='penulis', secondary='author_book')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(10), nullable=False, unique=True)
    password = db.Column(db.String(10), nullable=False, unique=True)
    admin = db.Column(db.Boolean)
    public_id = db.Column(db.String, nullable=False)

class Rent(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, nullable=False)
    date_rent = db.Column(db.Date)
    date_return = db.Column(db.Date)
    public_id = db.Column(db.String, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)

 

# # create table default
# db.create_all()
# db.session.commit()






# # authorization get_auth
def get_auth(auth):
    encode_var = base64.b64decode(auth[6:])
    string_var = encode_var.decode('ascii')
    lst = string_var.split(':')
    users = lst[0]
    passes = lst[1]
    user = User.query.filter_by(username=users).filter_by(password=passes).first()
    if not user:
        return {
            'message': 'None user in database'
        }
    elif user.admin is True:
        return 'True'
    elif not user.admin:
        return 'False'        

# # authorization auth_admin
def auth_admin(auth):
    base = base64.b64decode(auth[6:])
    decode = base.decode("ascii")
    lis = decode.split(':')
    username = lis[0]

    return username




# # path rents
@app.route('/rents', methods=['GET'])
def get_rent():
    decode_var = request.headers.get('Authorization')
    allow = get_auth(decode_var)
    if allow == 'True':
        return jsonify([
            {
            'name': rent.name,
            'date_rent': rent.date_rent,
            'date_return': rent.date_return,
            'buku': {
                'title': rent.buku.title,
                'release': rent.buku.release
            }
            } for rent in Rent.query.all()
        ]) 

    else:
        return {
            'message': 'Access denied'
        }, 401

@app.route('/rents', methods=['POST'])
def create_rent():
    decode_var = request.headers.get('Authorization')
    allow = get_auth(decode_var)
    if allow == 'True':
        data = request.get_json()
        for x in data['title']:   
            book_ = Book.query.filter_by(title=x).first_or_404()
            if book_.quantity == 0:
                return jsonify ({
                    'message': 'Book not available'
                }), 400

        admin = auth_admin(decode_var)
        admin = User.query.filter_by(username=admin).first()
        for y in data['title']:
            book = Book.query.filter_by(title=y).first()
            rent = Rent(
                name=data['name'],
                date_rent=data['date_rent'], 
                date_return=data['date_return'],
                book_id=book.id,
                admin_id=admin.id,
                public_id=str(uuid.uuid4())
            )
            book.quantity -= 1
        db.session.add(rent)
        db.session.commit()
        return {
            'message': 'success'
        }
    
    else:
        return {
            'message': 'Access denied'
        }, 401

@app.route('/rents/<id>', methods=['PUT'])
def update_rent(id):
    decode_var = request.headers.get('Authorization')
    allow = get_auth(decode_var)
    if allow == 'True':
        data = request.get_json()
        rent = Rent.query.filter_by(public_id=id).first_or_404()
        book = Book.query.filter_by(id=rent.book_id).first_or_404()
        rent.date_return = data['date_return']
        book.quantity += 1
        db.session.commit()
        return {
            'message': 'success'
        }

    else:
        return {
            'message': 'Access denied'
        }, 401



# # path home
@app.route('/home')
def home():
    return {
        'message':'WELCOME TO OUR BOOK LIBRARY'
    }




# # path User
@app.route('/users', methods=['GET'])
def get_user():
    decode_var = request.headers.get('Authorization')
    allow = get_auth(decode_var)
    if allow == 'True':
        return jsonify([
            {
            'id': user.public_id,
            'name': user.name,
            'username': user.username,
            'password': user.password
            } for user in User.query.all()
        ]) 

    else:
        return {
            'message': 'Access denied'
        }, 401

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if 'name' not in data:
        return jsonify ({
            'error': 'Bad Request',
            'message': 'name required'
        }), 400
    if len(data['username']) > 10 and len(data['password']) > 10:
        return jsonify ({
            'error': 'Bad Request',
            'message': 'must contain 10 character'
        }), 400
    u = User(
        name=data['name'],
        username=data['username'],
        password=data['password'],
        admin=data.get('admin'),
        public_id=str(uuid.uuid4())
        )

    db.session.add(u)
    db.session.commit()
    return jsonify ({
        'message': 'create user successfully'
    }), 201




# # path author_book
@app.route('/author_books') # get author_book data
def get_author_book():
    return jsonify([
        { 
            'id': book.public_id, 'title': book.title,
            'category': {
                'tag': book.categories.tag,
            },
            'author' : [
                x.name
                for x in book.penulis
            ]
        } for book in Book.query.all()
    ])


    # auth_author = db.relationship('Book', backref='penulis', secondary='author_book')


@app.route('/author_books', methods=['POST'])
def create_author_book():
    decode_var = request.headers.get('Authorization')
    allow = get_auth(decode_var)
    if allow == 'True':
        data = request.get_json()
        book = Book.query.filter_by(id=data['book_id']).first_or_404()
        author = Author.query.filter_by(id=data['author_id']).first_or_404()
        book.auth_book.append(author)
        db.session.add(book)
        db.session.commit()

        return {
            "message" : "success"
        },201
    
    else:
        return {
            'message': 'Access denied'
        }, 401




# # path Category
@app.route('/categories')
def get_categories():
    return jsonify([
        {
            'id': category.public_id, 'tag': category.tag, 'description': category.description
            } for category in Category.query.all()
    ])

@app.route('/categories/<id>/')
def get_category(id):
    print(id)
    category = Category.query.filter_by(public_id=id).first_or_404()
    return {
        'id': category.public_id, 'tag': category.tag, 'description': category.description
    }

# path query for insert,update,delete for category
@app.route('/categories', methods=['POST'])
def create_category():
    decode_var = request.headers.get('Authorization')
    allow = get_auth(decode_var)
    if allow == 'True':
        data = request.get_json()
        if not 'tag' in data or not 'description' in data:
            return jsonify ({
                'error': 'Bad Request',
                'message': 'There is no input'
            }), 400

        if len(data['tag']) == 0 or len(data['description']) == 0:
            return jsonify({
                'error': 'Bad Request',
                'message': 'tag and description must fill'
            }), 400
        
        c = Category(
            tag = data['tag'],
            description = data['description'],
            public_id = str(uuid.uuid4())
        )

        db.session.add(c)
        db.session.commit()
        return {
            'id': c.public_id, 'tag': c.tag, 'description': c.description
        }, 201

    else:
        return {
            'message': 'Access denied'
        }, 401

@app.route('/categories/<id>/', methods=['PUT'])
def update_category(id):
    decode_var = request.headers.get('Authorization')
    allow = get_auth(decode_var)
    if allow == 'True':
        data = request.get_json()
        if 'tag' not in data:
            return {
                'error': 'Bad Request',
                'message': 'Tag needs'
            }, 400

        category = Category.query.filter_by(public_id=id).first_or_404()
        category.tag = data['tag']
        category.description = data['description']
        db.session.commit()
        return jsonify ({
            'id': category.public_id, 'tag': category.tag, 'description':category.description
        })

    else:
        return {
            'message': 'Access denied'
        }, 401

@app.route('/categories/<id>/', methods=['DELETE'])
def delete_category(id):
    decode_var = request.headers.get('Authorization')
    allow = get_auth(decode_var)
    if allow == 'True':
        category = Category.query.filter_by(public_id=id).first_or_404()
        db.session.delete(category)
        db.session.commit()
        return {
            'success': 'Data successfully delete'
        }

    else:
        return {
            'message': 'Access denied'
        }, 401




# # path Book
@app.route('/books')
def get_books():
    return jsonify([
        {
            'id': book.public_id, 'title': book.title, 'release': book.release, 'quantity': book.quantity,
            'ketegori' : {
                'tag': book.kategori.tag,
                'description': book.kategori.description
            }
        } for book in Book.query.all()
    ])

@app.route('/books/<id>/')
def get_book(id):
    book = Book.query.filter_by(public_id=id).first_or_404()
    return jsonify ({
        'id': book.public_id, 'title': book.title, 'release': book.release, 
        'ketegori' : {
            'tag': book.kategori.tag,
            'description': book.kategori.description
        }        
    })

# path query for insert,update,delete for book
@app.route('/books', methods=['POST'])
def create_book():
    decode_var = request.headers.get('Authorization')
    allow = get_auth(decode_var)
    if allow == 'True':
        data = request.get_json()
        if not 'title' in data or not 'release' in data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'There is no input' 
            }), 400

        if len(data['title']) == 0 or len(data['release']) == 0:
            return jsonify({
                'error': 'Bad Request',
                'message': 'title and release must fill'
            }), 400

        category = Category.query.filter_by(tag=data['tag']).first()
        if not category:
            return {
                'error': 'Bad Request',
                'message': 'Invalid Tag' 
            }
        book = Book(
            title = data['title'],
            release = data['release'],
            categories_id = category.id,
            quantity = data['quantity'],
            public_id = str(uuid.uuid4())
        )
        db.session.add(book)
        db.session.commit()
        return {
            'id': book.public_id, 'title': book.title, 'release': book.release,
            'kategori':{
                'tag': book.kategori.tag,
                'description': book.kategori.description            
            }
        }, 201

    else:
        return {
            'message': 'Access denied'
        }, 401        

@app.route('/books/tag', methods=['POST']) # get data tag
def get_book_tag():
    data = request.get_json()
    categories = Category.query.filter_by(tag=data['tag']).first_or_404()
    b = []
    for x in categories.buku:
        b.append(x.title)
    return {
        'tag': categories.tag, 'books': b
    }

@app.route('/books/<id>/', methods=['PUT'])
def update_book(id):
    decode_var = request.headers.get('Authorization')
    allow = get_auth(decode_var)
    if allow == 'True':    
        data = request.get_json()
        print(data)
        print('title' in data)
        if not 'title' in data:
            return {
                'error': 'Bad Request',
                'message': 'Title needs'
            }, 400
        book = Book.query.filter_by(public_id=id).first_or_404()
        book.title = data.get('title', book.title)
        book.release = data.get('release', book.release)
        book.quantity = data.get('quantity', book.quantity)
        if 'categories_id' in data:
            book.categories_id = data['categories_id']
        db.session.commit()
        return {
            'id': book.public_id, 'title': book.title, 'release': book.release, 'quantity': book.quantity,
            'kategori':{
                'tag': book.kategori.tag,
                'description': book.kategori.description            
            }
        }, 201

    else:
        return {
            'message': 'Access denied'
        }, 401

@app.route('/books/<id>/', methods=['DELETE'])
def delete_book(id):
    decode_var = request.headers.get('Authorization')
    allow = get_auth(decode_var)
    if allow == 'True':    
        book = Book.query.filter_by(public_id=id).first_or_404()
        db.session.delete(book)
        db.session.commit()
        return {
            'success': 'Data successfully delete'
        }

    else:
        return {
            'message': 'Access denied'
        }, 401




# # path Author
@app.route('/authors')
def get_author():
    return jsonify ([
        {
            'id': author.public_id, 'name': author.name, 'bod': author.bod
        } for author in Author.query.all()
    ])

@app.route('/authors/<id>/')
def get_authors(id):
    author = Author.query.filter_by(public_id=id).first_or_404()
    return {
            'id': author.public_id, 'name': author.name, 'bod': author.bod        
    }

# path query for insert,update,delete for author
@app.route('/authors', methods=['POST'])
def create_author():
    decode_var = request.headers.get('Authorization')
    allow = get_auth(decode_var)
    if allow == 'True':    
        data = request.get_json()
        if not 'name' in data or not 'bod' in data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'There is no input'
            }), 400

        if len(data['name']) == 0 or len(data['bod']) == 0:
            return jsonify ({
                'error': 'Bad Request',
                'message': 'name and bod must fill'
            }), 400

        a = Author(
            name = data['name'],
            bod = data['bod'],
            public_id = str(uuid.uuid4())
        )

        db.session.add(a)
        db.session.commit()
        return {
                'id': a.public_id, 'name': a.name, 'bod': a.bod             
        }, 201

    else:
        return {
            'message': 'Access denied'
        }, 401

@app.route('/authors/<id>/', methods=['PUT'])
def update_author(id):
    decode_var = request.headers.get('Authorization')
    allow = get_auth(decode_var)
    if allow == 'True':    
        data = request.get_json()
        if 'name' not in data:
            return {
                'error': 'Bad Request',
                'message': 'Name needs'
            }, 400

        author = Author.query.filter_by(public_id=id).first_or_404()
        author.name = data['name']
        author.bod = data['bod']
        db.session.commit()
        return jsonify ({
            'id': author.public_id, 'name': author.name, 'bod':author.bod
        })

    else:
        return {
            'message': 'Access denied'
        }, 401

@app.route('/authors/<id>/', methods=['DELETE'])
def delete_author(id):
    decode_var = request.headers.get('Authorization')
    allow = get_auth(decode_var)
    if allow == 'True':    
        author = Author.query.filter_by(public_id=id).first_or_404()
        db.session.delete(author)
        db.session.commit()
        return {
            'success': 'Data successfully delete'
        }

    else:
        return {
            'message': 'Access denied'
        }, 401
