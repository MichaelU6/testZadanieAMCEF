import requests
from flask import Flask, jsonify, request, render_template, flash, redirect, url_for, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource, fields

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Konfigurácia pre SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # URI pre SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Vytvorenie Blueprint pre dokumentáciu API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Inicializácia Swagger API dokumentácie
api = Api(api_bp, version='1.0', title='API Dokumentácia', description='Dokumentácia pre API')

# Externé URL
BASE_URL = "https://jsonplaceholder.typicode.com"

# Trieda pre model príspevku
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer)
    title = db.Column(db.String(100))
    body = db.Column(db.String(1000))

with app.app_context():
    db.drop_all()
    db.create_all()

# Validácia userID pomocou externého API
def validate_user(user_id):
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    if response.status_code == 200:
        return True
    return False

# Zobrazenie domovskej stránky
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

#Page na vybratie zobrazovaneho príspevku
@app.route('/page2')
def view_page():
    return render_template('viewpost.html')

#Ziskanie id zobrazovaného príspevku
@app.route('/numberpost', methods=['POST'])
def takeID():
    post_data = request.form
    post_id = post_data['id']
    search_type = post_data['search_type']
    if search_type == 'id':
        url = url_for('get_post_or_posts_by_user', post_id=post_id)
    else:
        url = url_for('get_post_or_posts_by_user', user_id=post_id)
    return redirect(url)

# Získanie príspevkov na základe ID alebo userID
@app.route('/posts/<int:post_id>', methods=['GET'])
@app.route('/posts/user/<int:user_id>', methods=['GET'])
def get_post_or_posts_by_user(post_id=None, user_id=None):
    if post_id:
        post = Post.query.filter_by(id=post_id).all()
        if post:
            return render_template('posts.html', posts=post[0])
        else:
            response = requests.get(f"{BASE_URL}/posts/{post_id}")
            if response.status_code == 200:
                new_post = Post(
                    id=response.json()['id'],
                    userId=response.json()['userId'],
                    title=response.json()['title'],
                    body=response.json()['body']
                )
                db.session.add(new_post)
                db.session.commit()
                return render_template('posts.html', posts=new_post)
            else:
                flash('Vyskytol sa problém.', 'error')
                return redirect(url_for('home'))
    elif user_id:
        user_posts = Post.query.filter_by(userId=user_id).all()
        if user_posts:
            return render_template('userPosts.html', posts=user_posts)
        else:
            flash('Užívateľ nemá žiadny príspevok.', 'error')
            return redirect(url_for('home'))

# Pridanie nového príspevku s validáciou userID
@app.route('/page1')
def add_page():
    return render_template('add.html')

@app.route('/add-post', methods=['POST'])
def add_post():
    post_data = request.form
    user_id = post_data['userId']
    if validate_user(user_id):
        new_post = Post(
            userId=user_id,
            title=post_data['title'],
            body=post_data['body']
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Príspevok bol úspešne pridaný.', 'success')
        return redirect(url_for('home'))
    else:
        flash('Neplatný userID.', 'error')
        return redirect(url_for('home'))

# Odstránenie príspevku
@app.route('/delete-post/<int:post_id>', methods=['GET', 'DELETE'])
def delete_post(post_id):
    post = Post.query.get(post_id)
    if post:
        db.session.delete(post)
        db.session.commit()
        flash('Príspevok bol odstránený.', 'success')
        return redirect(url_for('home'))
    else:
        flash('Príspevok nenájdený.', 'error')
        return redirect(url_for('home'))

# Úprava príspevku
@app.route('/updatepost/<int:post_id>', methods=['GET', 'PUT'])
def update_page(post_id):
    return render_template('change.html', post_id=post_id)

@app.route('/update_page/<int:post_id>', methods=['POST', 'PUT'])
def update_post(post_id):
    post = Post.query.get(post_id)
    if post:
        post_data = request.form
        post.title = post_data['title']
        post.body = post_data['body']
        db.session.commit()
        flash('Príspevok bol upravený.', 'success')
        return redirect(url_for('home'))
    else:
        flash('Príspevok nenájdený.', 'error')
        return redirect(url_for('home'))



# Model pre vytvorenie príspevku
create_post_model = api.model('CreatePost', {
    'userId': fields.Integer(required=True, description='ID používateľa'),
    'title': fields.String(required=True, description='Názov príspevku'),
    'body': fields.String(required=True, description='Obsah príspevku')
})

# Model pre aktualizáciu príspevku
update_post_model = api.model('UpdatePost', {
    'title': fields.String(description='Názov príspevku'),
    'body': fields.String(description='Obsah príspevku')
})
# Endpoint pre príspevky
@api.route('/posts/<int:post_id>')
class PostResource(Resource):
    @api.doc(description='Získanie príspevku podľa ID')
    @api.response(200, 'Úspešne získaný príspevok')
    @api.response(404, 'Príspevok nenájdený')
    def get(self, post_id):
        """
        Získanie príspevku podľa ID
        """
        post = Post.query.get(post_id)
        if post:
            return {'id': post.id, 'userId': post.userId, 'title': post.title, 'body': post.body}, 200
        else:
            api.abort(404, 'Príspevok nenájdený')

    @api.doc(description='Odstránenie príspevku podľa ID')
    @api.response(204, 'Príspevok úspešne odstránený')
    @api.response(404, 'Príspevok nenájdený')
    def delete(self, post_id):
        """
        Odstránenie príspevku podľa ID
        """
        post = Post.query.get(post_id)
        if post:
            db.session.delete(post)
            db.session.commit()
            flash('Príspevok bol úspešne odstránený.', 'success')
            return None, 204
        else:
            api.abort(404, 'Príspevok nenájdený')

    @api.doc(description='Aktualizácia príspevku podľa ID')
    @api.expect(update_post_model)
    @api.response(200, 'Príspevok bol úspešne aktualizovaný')
    @api.response(400, 'Chybná požiadavka')
    @api.response(404, 'Príspevok nenájdený')
    def put(self, post_id):
        post = Post.query.get(post_id)
        if post:
            post_data = request.json
            post.title = post_data.get('title', post.title)
            post.body = post_data.get('body', post.body)
            db.session.commit()
            flash('Príspevok bol úspešne aktualizovaný.', 'success')
            return '', 200
        else:
            flash('Príspevok nenájdený.', 'error')
            return {'message': 'Príspevok nenájdený'}, 404

# Endpoint pre pridanie príspevku
@api.route('/posts')
class CreatePostResource(Resource):
    @api.doc(description='Pridanie nového príspevku')
    @api.expect(create_post_model)
    @api.response(201, 'Príspevok bol úspešne vytvorený')
    @api.response(400, 'Chybná požiadavka')
    def post(self):
        post_data = request.json
        user_id = post_data['userId']
        if validate_user(user_id):
            new_post = Post(
                userId=user_id,
                title=post_data['title'],
                body=post_data['body']
            )
            db.session.add(new_post)
            db.session.commit()
            flash('Príspevok bol úspešne vytvorený.', 'success')
            return '', 201
        else:
            flash('Neplatný userID.', 'error')
            return {'message': 'Neplatný userID.'}, 400


# Pripojenie Blueprint pre dokumentáciu API k aplikácii
app.register_blueprint(api_bp)

# Spustenie aplikácie
if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0")
