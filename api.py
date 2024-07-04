from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
#marshal_width helps to send a json data back in a serialized format. Basically its a decorator

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' #naming our database
db = SQLAlchemy(app)
#define our api with flask restful
api = Api(app)

#modeling the data
class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), unique = True, nullable = False)
    email = db.Column(db.String(80), unique = True, nullable = False)

    # representation
    def __repr__(self):
        return f"User(name = {self.name}, email = {self.name})"

# validate the user data using reqparse 
user_args  = reqparse.RequestParser()
user_args.add_argument('name', type=str, required = True, help= 'name cannot be blank')
user_args.add_argument('email', type=str, required = True, help= 'email cannot be blank')
#define a route, write a func that runs after this route

# marshalling/ serializable(convert to json data)
userFields = {
        'id': fields.Integer,
        'name': fields.String,
        'email': fields.String,

}
class Users(Resource):
    @marshal_with(userFields) #do this decor with everyone sending the data back
    def get(self):
        users = UserModel.query.all()
        return users
    
    @marshal_with(userFields) #do this decor with 
    def post(self):
        args = user_args.parse_args()
        user = UserModel(name = args["name"], email = args["email"])
        db.session.add(user)
        db.session.commit()
        #get all users
        users = UserModel.query.all()
        return users, 201 # 201 is the https status

class User(Resource):
    @marshal_with(userFields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, "user not found")
        return user
    
    @marshal_with(userFields)
    def patch(self, id):
        #use parse when we recieve user arguements to check if the data is valid
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, "user not found")
        user.name = args["name"]
        user.email = args["email"]
        db.session.commit()
        return user
    
    @marshal_with(userFields)
    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, "user not found")
        db.session.delete(user)
        db.session.commit()
        users = UserModel.query.all()
        return users, 204
        

#assign end point to a url
api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:id>')
@app.route('/')
def home():
    return '<h1>Flask Rest API</h1>'

if __name__ == '__main__':
    app.run(debug=True)
