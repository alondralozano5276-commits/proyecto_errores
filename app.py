import logging
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_login import LoginManager, login_required, current_user
from flask_restful import Api
from werkzeug.exceptions import HTTPException, BadRequest, MethodNotAllowed
from models import db, User
import controllers

sentry_sdk.init(
    dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
    integrations=[FlaskIntegration()]
)

app = Flask(__name__)

file_handler = logging.FileHandler('errors.log')
file_handler.setLevel(logging.ERROR)
app.logger.addHandler(file_handler)

app.config['SECRET_KEY'] = 'clave_secreta_muy_segura_12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:hola1234@localhost/juegos'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.session_protection = 'strong'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')

from api.routes import JuegoList, JuegoResource
api = Api(app, prefix='/api')
api.add_resource(JuegoList, '/juegos')
api.add_resource(JuegoResource, '/juegos/<int:id>')

@app.errorhandler(BadRequest)
def handle_400(e):
    return '<div style="text-align:center; margin-top:50px; font-family:sans-serif;"><h1 style="color:red; font-size:48px;">Error 400</h1><h2>Solicitud Incorrecta (Bad Request)</h2><p>La solicitud enviada contiene sintaxis o parametros invalidos.</p></div>', 400

@app.errorhandler(404)
def handle_404(e):
    return '<div style="text-align:center; margin-top:50px; font-family:sans-serif;"><h1 style="color:orange; font-size:48px;">Error 404</h1><h2>Pagina No Encontrada</h2><p>El recurso que buscas no existe en el servidor.</p></div>', 404

@app.errorhandler(MethodNotAllowed)
def handle_405(e):
    return '<div style="text-align:center; margin-top:50px; font-family:sans-serif;"><h1 style="color:blue; font-size:48px;">Error 405</h1><h2>Metodo No Permitido</h2><p>El metodo HTTP utilizado no esta permitido en esta ruta.</p></div>', 405

@app.errorhandler(500)
def handle_500(e):
    return '<div style="text-align:center; margin-top:50px; font-family:sans-serif;"><h1 style="color:darkred; font-size:48px;">Error 500</h1><h2>Error Interno del Servidor</h2><p>Ocurrio un error inesperado en el servidor.</p></div>', 500

@app.errorhandler(HTTPException)
def handle_api_error(e):
    if request.path.startswith('/api/'):
        response = e.get_response()
        response.data = jsonify(code=e.code, name=e.name, description=e.description).data
        response.content_type = 'application/json'
        return response
    return e

@app.route("/")
@app.route("/juegos")
@login_required
def juegos():
    lista_juegos = controllers.obtener_juegos()
    return render_template("juegos.html", juegos=lista_juegos)

@app.route("/videogame/<int:id>")
def ver_videojuego(id):
    parametro = request.args.get("ref")
    if not parametro:
        abort(400)
    return f"Videojuego {id} cargado con exito"

@app.route("/error_forzado")
def error_forzado():
    resultado = 1 / 0
    return str(resultado)

@app.route("/agregar_juego")
@login_required
def formulario_agregar_juego():
    return render_template("agregar_juego.html")

@app.route("/guardar_juego", methods=["POST"])
@login_required
def guardar_juego():
    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]
    precio = request.form["precio"]
    controllers.insertar_juego(nombre, descripcion, precio)
    return redirect(url_for("juegos"))

@app.route("/eliminar_juego", methods=["POST"])
@login_required
def eliminar_juego():
    id = request.form["id"]
    controllers.eliminar_juego(id)
    return redirect(url_for("juegos"))

@app.route("/formulario_editar_juego/<int:id>")
@login_required
def editar_juego(id):
    juego = controllers.obtener_juego_por_id(id)
    return render_template("editar_juego.html", juego=juego)

@app.route("/actualizar_juego", methods=["POST"])
@login_required
def actualizar_juego():
    id = request.form["id"]
    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]
    precio = request.form["precio"]
    controllers.actualizar_juego(id, nombre, descripcion, precio)
    return redirect(url_for("juegos"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=8000, debug=False)