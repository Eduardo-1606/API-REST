from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
import os


app = Flask(__name__)

#Configuracion de la base de datos MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:admin@localhost:5432/contact'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialización de la base de datos y el serializador
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)


#Modelo de Contacto
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(100), nullable = False)
    numero_telefono = db.Column(db.String(20), unique = True, nullable= False)
    email = db.Column(db.String(100), unique = True, nullable = False)

    def __init__(self, nombre, numero_telefono, email):
        self.nombre = nombre
        self.numero_telefono = numero_telefono
        self.email = email

#Esquema de Contacto
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
class ContactSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Contact

contact_schema = ContactSchema()
contacts_schema = ContactSchema( many = True )

#Endpoint para obtener todos los contactos
@app.route('/contacts', methods=['GET'])
def get_contacts():
    all_contacts = Contact.query.all()
    result = contacts_schema.dump(all_contacts)
    return jsonify(result)

#Endpoint para la paginación de contactos
@app.route('/contacts/page', methods=['GET'])
def get_paginacion_contacto():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    contacts = Contact.query.paginate(page, page_size, error_out=False).items
    result = contacts_schema.dump(contacts)
    return jsonify(result)

#Endpoint para obtener un contacto por ID
@app.route('/contact/<id>', methods=['GET'])
def get_contact(id):
    contact = Contact.query.get(id)
    if contact is None:
        return jsonify({'message': 'Contacto no encontrado'}), 404
    return contact_schema.jsonify(contact)

#Endpoint para crear un nuevo contacto
@app.route('/contact', methods=['POST'])
def agregar_contacto():
    if request.content_type != 'application/json':
        return jsonify({'message':'El tipo de contendio debe ser applications/json'})
    
    nombre = request.json.get('nombre')
    numero_telefono = request.json.get('numero_telefono') 
    email = request.json.get('email')

    if not nombre or not numero_telefono or not email:
        return jsonify({'message':'Contacto agregado'})
    
    nuevo_contacto = Contact(nombre=nombre, numero_telefono=numero_telefono, email=email)

    try:
        db.session.add(nuevo_contacto)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message':'Error al agregar contacto', 'error':str(e)}),500
    
    return contact_schema.jsonify(nuevo_contacto),201


#Endpoint para modificiar un contacto existente
@app.route('/contact/<id>', methods=['PUT'])
def update_contact():
    contact = Contact.query.get(id)
    if contact is None:
        return jsonify({'message': 'Contacto no encontrado'}), 404
    
    contact.nombre = request.json.get('nombre', contact.nombre)
    contact.numero_telefono = request.json.get('numero_telefono', contact.numero_telegono)
    contact.email = request.json.get('email', contact.email)

    db.session.commit()
    return contact_schema.jsonify(contact)

#Endpoint para eliminar un contacto
@app.route('/contact/<id>', methods=['DELETE'])
def delete_contact(id):
    contact = Contact.query.get(id)
    if contact is None:
        return jsonify({'message': 'Contacto no econtrado'}), 400
    
    db.session.delete(contact)
    db.session.commit()
    return jsonify({'message': 'Contacto eliminado'})

#Ejecucion de la aplicacion
if __name__ == '__main__':
    app.run(debug = True)




