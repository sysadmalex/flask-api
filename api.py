from asyncio.proactor_events import _ProactorBasePipeTransport
import os
import json
 
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import dotenv
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from marshmallow import Schema, fields
 
dotenv.load_dotenv()
 
db_user = os.environ.get('DB_USERNAME')
db_pass = os.environ.get('DB_PASSWORD')
db_hostname = os.environ.get('DB_HOSTNAME')
db_name = os.environ.get('DB_NAME')
 
DB_URI = 'mysql+pymysql://{db_username}:{db_password}@{db_host}/{database}'.format(db_username=db_user, db_password=db_pass, db_host=db_hostname, database=db_name)
 
engine = create_engine(DB_URI, echo=True)
 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
 
class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    cellphone = db.Column(db.String(13), unique=True, nullable=False)
 
    @classmethod
    def get_all(cls):
        return cls.query.all()
 
    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)
 
    def save(self):
        db.session.add(self)
        db.session.commit()
 
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()
 
class StudentSchema(Schema):
    id = fields.Integer()
    name = fields.Str()
    email = fields.Str()
    age = fields.Integer()
    cellphone = fields.Str()
 
@app.route('/', methods = ['GET'])
def home():
    return '<p>Hello from students API!</p>', 200
 
@app.route('/api', methods = ['GET'])
def api_main():
    with open('info.json', 'r', encoding='utf-8') as info:
        json_data = json.load(info)
    return jsonify('Hello, World!'), 200
     
@app.route('/api/students', methods=['GET'])
def get_all_students():
    students = Student.get_all()
    student_list = StudentSchema(many=True)
    response = student_list.dump(students)
    return jsonify(response), 200
 
@app.route('/api/students/get/<int:id>', methods = ['GET'])
def get_student(id):
    student_info = Student.query.filter(Student.id == id).one_or_none()
    if student_info:
        serializer = StudentSchema()
        response = serializer.dump(student_info)
        return jsonify(response), 200
    else:
        return jsonify(message='No student with ID {} in base'.format(id)), 404
 
@app.route('/api/students/add', methods = ['POST'])
def add_student():
    json_data = request.get_json()
    new_student = Student(
        name= json_data.get('name'),
        email=json_data.get('email'),
        age=json_data.get('age'),
        cellphone=json_data.get('cellphone')
    )
    new_student.save()
    serializer = StudentSchema()
    data = serializer.dump(new_student)
    return jsonify(data), 201

@app.route('/api/students/modify/<int:id>', methods = ['PATCH'])
def modify_student(id):
   if request.method == 'PATCH':
        json_data = request.get_json()
        student_modify = Student.query.filter(Student.id == id).one_or_none()
        if student_modify:
            if "name" in json_data:
                student_modify.name = json_data.get('name')
            if "email" in json_data:
                student_modify.email = json_data.get('email')
            if "age" in json_data:
                student_modify.age = json_data.get('age')
            if "cellphone" in json_data:
                student_modify.cellphone = json_data.get('cellphone')
            student_modify.update()
            serializer = StudentSchema()
            data = serializer.dump(student_modify)
            return jsonify(data), 201
        
@app.route('/api/students/change/<int:id>', methods = ['PUT'])
def change_student(id):
    if request.method == 'PUT':
        student_change = Student.query.filter(Student.id == id).one_or_none()
        if student_change:
            json_data = request.get_json()
            student_change.name = json_data.get('name')
            student_change.email = json_data.get('email')
            student_change.age = json_data.get('age')
            student_change.cellphone = json_data.get('cellphone')
            student_change.update()
            serializer = StudentSchema()
            data = serializer.dump(student_change)
            return jsonify(data), 201
           
@app.route('/api/students/delete/<int:id>', methods = ['DELETE'])
def delete_student(id):
    if request.method == 'DELETE':
        delete_student = Student.query.filter(Student.id == id).one_or_none()
        if delete_student:
            delete_student.delete()
            return jsonify(message='Student with ID:{} deleted'.format(id)), 200
        else:
            return jsonify(message='Student with ID:{} not found in database'.format(id)), 404



@app.route('/api/health-check/ok', methods = ['GET'])
def health_check_ok():
    return jsonify(message='Health is OK'), 200

@app.route('/api/health-check/bad', methods = ['GET'])
def health_check_bad():
    return jsonify(message='Health is BAD'), 404 

if __name__ == '__main__':
    if not database_exists(engine.url):
        create_database(engine.url)
    db.create_all()
    app.run(use_reloader=True, debug=True)


    