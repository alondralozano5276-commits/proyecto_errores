from flask_restful import Resource, reqparse
from models import db, Juego

parser = reqparse.RequestParser()
parser.add_argument('nombre', type=str, required=True, help="El nombre es obligatorio")
parser.add_argument('descripcion', type=str, required=True, help="La descripción es obligatoria")
parser.add_argument('precio', type=float, required=True, help="El precio es obligatorio y debe ser numérico")

class JuegoList(Resource):
    def get(self):
        """
        Obtener todos los juegos (GET /api/juegos) - 200 OK
        """
        juegos = Juego.query.all()
        return [juego.to_json() for juego in juegos], 200

    def post(self):
        """
        Crear un juego nuevo enviando JSON (POST /api/juegos) - 201 Created
        """
        data = parser.parse_args()
        nuevo_juego = Juego(
            nombre=data['nombre'],
            descripcion=data['descripcion'],
            precio=data['precio']
        )
        db.session.add(nuevo_juego)
        db.session.commit()
        return nuevo_juego.to_json(), 201


class JuegoResource(Resource):
    def get(self, id):
        """
        Obtener un juego por ID (GET /api/juegos/<id>)
        """
        juego = Juego.query.get(id)
        if not juego:
            return {'error': 'Juego no encontrado'}, 404
        return juego.to_json(), 200

    def put(self, id):
        """
        Modificar un juego existente (PUT /api/juegos/<id>)
        """
        juego = Juego.query.get(id)
        if not juego:
            return {'error': 'Juego no encontrado'}, 404

        data = parser.parse_args()
        juego.nombre = data['nombre']
        juego.descripcion = data['descripcion']
        juego.precio = data['precio']
        db.session.commit()
        return juego.to_json(), 200

    def delete(self, id):
        """
        Eliminar un juego (DELETE /api/juegos/<id>) - 204 No Content
        """
        juego = Juego.query.get(id)
        if not juego:
            return {'error': 'Juego no encontrado'}, 404

        db.session.delete(juego)
        db.session.commit()
        return '', 204