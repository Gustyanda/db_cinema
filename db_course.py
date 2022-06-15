from flask import Flask, request, jsonify, request_started
from flask_sqlalchemy import SQLAlchemy
import uuid, base64
app=Flask(__name__)
db=SQLAlchemy(app)

app.config['SECRET_KEY']='secret'
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:Kehidupan6@localhost:5432/db_course?sslmode=disable'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True




instructor_course=db.Table('instructor_course',
    db.Column('instructor_id', db.Integer, db.ForeignKey('instructor.id'), nullable=False),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), nullable=False))

class Category(db.Model):
    id=db.Column(db.Integer, primary_key=True, index=True)
    public_id=db.Column(db.String, nullable=False)
    tag=db.Column(db.String, nullable=False)
    course=db.relationship('Course', backref='categories')

class Course(db.Model):
    id=db.Column(db.Integer, primary_key=True, index=True)
    public_id=db.Column(db.String, nullable=False)
    lesson=db.Column(db.String, nullable=False)
    categories_id=db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    categories_=db.relationship('Category', backref='courses')
    associate_c=db.relationship('Instructor', backref='associate_c', secondary='instructor_course')
    enroll=db.relationship('Enroll', backref='course_')

class Instructor(db.Model):
    id=db.Column(db.Integer, primary_key=True, index=True)
    public_id=db.Column(db.String, nullable=False)
    coach=db.Column(db.String, nullable=False)
    username=db.Column(db.String, nullable=False, unique=True)
    password=db.Column(db.String, nullable=False, unique=True)
    status=db.Column(db.Boolean)
    associate_i=db.relationship('Course', backref='associate_i', secondary='instructor_course')

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True, index=True)
    public_id=db.Column(db.String, nullable=False)
    name=db.Column(db.String, nullable=False)
    username=db.Column(db.String, nullable=False, unique=True)
    password=db.Column(db.String, nullable=False, unique=True)
    enroll=db.relationship('Enroll', backref='user_')

class Enroll(db.Model):
    id=db.Column(db.Integer, primary_key=True, index=True)
    public_id=db.Column(db.String, nullable=False)
    status=db.Column(db.String)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id=db.Column(db.Integer, db.ForeignKey('course.id'))





# --------------- create table default
db.create_all()
db.session.commit()



# --------------- authorization for user
def auth_user(auth): 
    encode = base64.b64decode(auth[6:])
    str_encode = encode.decode('ascii')
    lst = str_encode.split(':')
    users = lst[0]
    passes = lst[1]   
    user = User.query.filter_by(username=users).filter_by(password=passes).first()
    if user:
        return  str(user.public_id)
    else:
        return 0

# --------------- authorization for coach
def auth_coach(auth):
    encode = base64.b64decode(auth[6:])
    str_encode = encode.decode('ascii')
    lst = str_encode.split(':')
    users = lst[0]
    passes = lst[1]   
    instructor = Instructor.query.filter_by(username=users).filter_by(password=passes).first()
    if instructor:
        return  str(instructor.public_id)
    else:
        return 0

# --------------- authorization for coach admin
def auth_coach_admin(auth):
    encode = base64.b64decode(auth[6:])
    str_encode = encode.decode('ascii')
    lst = str_encode.split(':')
    users = lst[0]
    passes = lst[1]   
    instructor = Instructor.query.filter_by(username=users).filter_by(password=passes).first()
    if not instructor:
        return {
            'message': 'None user in database !' 
        }
    elif instructor.status is True:
        return True
    elif not instructor.status:
        return False     



# --------------- API - Home
@app.route('/', methods=['GET'])
def home():
    return {
        'message': 'WELCOME TO COURSE ONLINE'
    }




# --------------- API - category
@app.route('/category', methods=['GET'])
def get_category():
    return jsonify ([
        { 
            'tag':category.tag
        } for category in Category.query.all()
    ])

@app.route('/category', methods=['POST'])
def create_category():
    data = request.get_json()
    if len(data['tag']) == 0:
        return {
            'message': 'must fill tag detail !'
        }, 400
    
    c = Category(
        public_id=str(uuid.uuid4()),
        tag=data['tag']
    )

    db.session.add(c)
    db.session.commit()
    return {
        'message': 'tag successfully create'
    }, 201




# --------------- API - course
@app.route('/course', methods=['GET'])
def get_course():
    return jsonify ([
        {
            'lesson':course.lesson,
            'categories':{
                'tag': course.categories.tag
            },
            'instructors':[
                {
                'coach': x.coach
                    
                } for x in course.associate_i
            ]
        } for course in Course.query.all()
    ])

@app.route('/course/<id>', methods=['POST']) # authorization separated by public_id coach
def create_course_id(id):
    decode = request.headers.get('Authorization')
    allow = auth_coach(decode)
    if allow == id:
        data = request.get_json()
        if len(data['lesson']) == 0:
            return {
                'message': 'must fill lesson detail !'
            }, 400

        category = Category.query.filter_by(tag=data['tag']).first()
        if not category:
            return {
                'message': 'tag needs !'
            }, 400

        c = Course(
            public_id=str(uuid.uuid4()),
            lesson=data['lesson'],
            categories_id=category.id
        )
        db.session.add(c)
        db.session.commit()
        return {
            'message': 'lesson successfully create !'
        }, 201
    else:
        return {
            'message': 'un-authorized user is denied !'
        }, 400        

  


# --------------- API - instructor
@app.route('/instructor', methods=['GET'])
def get_instructor():
    return jsonify([
        {
            'coach':instructor.coach
        } for instructor in Instructor.query.all()
    ])

@app.route('/instructor', methods=['POST'])  # authorization separated by admin coach
def create_instructor():
    decode = request.headers.get('Authorization')
    allow = auth_coach_admin(decode)
    if allow == True:
        data = request.get_json()
        if len(data['coach']) == 0:
            return {
                'message': 'name instructor required !'
            }, 400

        i = Instructor(
            public_id=str(uuid.uuid4()),
            coach=data['coach'],
            username=data['username'],
            password=data['password'],
            status=data['status']
        )
        db.session.add(i)
        db.session.commit()
        return {
            'message': 'instructor successfully add !'
        }, 201
    else:
        return {
            'message': 'Access denied'
        }, 401  

@app.route('/instructor/<id>', methods=['GET']) # authorization separated by public_id coach
def get_instructor_id(id):
    decode = request.headers.get('Authorization')
    allow = auth_coach(decode)
    if allow == id:
        instructor = Instructor.query.filter_by(public_id=id).first_or_404()
        return jsonify ({
            'coach':instructor.coach, 'username':instructor.username, 'password':instructor.password, 'status':instructor.status
        })
    else:
        return {
            'message': 'un-authorized user is denied !'
        }, 400

@app.route('/instructor/<id>', methods=['PUT']) # authorization separated by public_id coach
def update_instructor_id(id):
    decode = request.headers.get('Authorization')
    allow = auth_coach(decode)
    if allow == id:
        data = request.get_json()
        instructor = Instructor.query.filter_by(public_id=id).first_or_404()
        instructor.username = data['username']
        instructor.password = data['password']
        instructor.status = data['status']
        db.session.commit()
        return {
                'message': 'data has been update !'
            }
    return {
        'message': 'un-authorized user is denied !'
    }, 400    




# --------------- API - user
@app.route('/user', methods=['GET'])
def get_user():
    return jsonify ([
        {
            'name':user.name, 'username':user.username
        } for user in User.query.all()
    ])

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    if len(data['name']) == 0:
        return {
            'message': 'name requirement for applicant student !'
        }, 400

    if len(data['username']) > 15 and len(data['password']) > 15:
        return {
            'message': 'username/password is too long !'
        }, 400

    u = User(
        public_id=str(uuid.uuid4()),
        name=data['name'],
        username=data['username'],
        password=data['password']
    )
    db.session.add(u)
    db.session.commit()
    return {
        'message': 'user successfully create !'
    }, 201

@app.route('/user/<id>', methods=['GET']) # authorization separated by public_id user
def get_user_id(id):
    decode = request.headers.get('Authorization')
    allow = auth_user(decode)
    if allow == id:
        user = User.query.filter_by(public_id=id).first_or_404()
        return jsonify ({
            'name':user.name, 'username':user.username, 'password':user.password
        })
    else:
        return {
            'message': 'un-authorized user is denied !'
        }, 400

@app.route('/user/<id>', methods=['PUT']) # authorization separated by public_id user
def update_user(id):
    decode = request.headers.get('Authorization')
    allow = auth_user(decode)
    if allow == id:
        data = request.get_json()
        user = User.query.filter_by(public_id=id).first_or_404()
        user.username = data['username']
        user.password = data['password']
        db.session.commit()
        return {
            'message': 'data has been update !'
        }
    else:
        return {
            'message': 'un-authorized user is denied !'
        }, 400    




# --------------- API - instructor_course
@app.route('/instructor_course', methods=['GET'])
def get_instructor_course():
    return jsonify([
        { 
            'lesson': course.lesson,
            'category': {
                'tag': course.categories_.tag,
            },
            'instructor' : [
                x.coach
                for x in course.associate_i
            ]
        } for course in Course.query.all()
    ])

@app.route('/instructor_course', methods=['POST'])  # authorization separated by admin coach
def create_instructor_course():
    decode = request.headers.get('Authorization')
    allow = auth_coach_admin(decode)
    if allow == True:
        data = request.get_json()
        course = Course.query.filter_by(id=data['course_id']).first()
        instructor = Instructor.query.filter_by(id=data['instructor_id']).first()
        course.associate_c.append(instructor)
        db.session.add(course)
        db.session.commit()
        return {
            "message" : "instructor for course has been assigned !"
        },201
    
    else:
        return {
            'message': 'Access denied'
        }, 401  
  



# --------------- API - enroll
@app.route('/enroll/<id>', methods=['GET']) # authorization separated by public_id user
def get_enroll(id):
    decode = request.headers.get('Authorization')
    allow = auth_user(decode)
    if allow == id:    
        return jsonify ([
            {
                'status': enroll.status,
                'name': enroll.user_.name ,
                'lesson': enroll.course_.lesson,
                # 'instructor': enroll.instructor.coach
            } for enroll in Enroll.query.all()
        ])
    return {
        'message': 'Access denied'
    }, 401

@app.route('/enroll/<id>', methods=['POST']) # authorization separated by public_id user
def create_enroll(id):
    decode = request.headers.get('Authorization')
    allow = auth_user(decode)
    if allow == id:    
        data = request.get_json()
        user = User.query.filter_by(name=data['name']).first()
        enroll = Enroll.query.filter_by(user_id=user.id).filter_by(status='Activate').count()
        if enroll == 3:
            return {
                'message': 'Maximum enroll 3 course !'
            }

        user = User.query.filter_by(name=data['name']).first()
        course = Course.query.filter_by(lesson=data['lesson']).first()
        # instructor = Instructor.query.filter_by(coach=data['coach']).first()
        e = Enroll(
            public_id=str(uuid.uuid4()),
            user_id=user.id,
            course_id=course.id,
            # instructor_id=instructor.id,
            status=data['status']
        )
        db.session.add(e)
        db.session.commit()
        return {
            'message': 'enroll submit success !'
        }, 201
    
    else:
        return {
            'message': 'un-authorized user is denied !'
        }, 400    

@app.route('/enroll/<id>', methods=['PUT']) # authorization separated by public_id user for status
def update_enroll(id):
    decode = request.headers.get('Authorization')
    allow = auth_user(decode)
    data = request.get_json()
    user = User.query.filter_by(public_id=allow).first()
    enroll = Enroll.query.filter_by(user_id=user.id).filter_by(course_id=id).first()
    if enroll:
        enroll.status = data['status']
        db.session.commit()
        return {
            'message': 'data has been update !'
        }
    else:
        return {
            'message': 'un-authorized user is denied !'
        }, 400 

    