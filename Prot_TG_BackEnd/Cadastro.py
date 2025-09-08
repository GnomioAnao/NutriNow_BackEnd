from flask import Flask, request, jsonify
import pymysql
from werkzeug.security import generate_password_hash
from flask_cors import CORS  # ← importe o módulo CORS

app = Flask(__name__)       # ← cria o app Flask
CORS(app)                   # ← habilita CORS para todas as rotas

db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '12345678',
    'database': 'nutrinow',
    'cursorclass': pymysql.cursors.DictCursor
}

# suas rotas aqui
@app.route('/', methods=['GET'])
def index():
    return 'Servidor Flask funcionando!'

# CREATE
@app.route('/criar-conta', methods=['POST'])
def criar_conta():
    data = request.get_json()
    nome = data.get('nome')
    sobrenome = data.get('sobrenome')
    data_nascimento = data.get('data_nascimento')
    genero = data.get('genero')
    email = data.get('email')
    senha = data.get('senha')

    if not all([nome, sobrenome, data_nascimento, genero, email, senha]):
        return jsonify({'error': 'Todos os campos são obrigatórios.'}), 400

    senha_hash = generate_password_hash(senha)

    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        sql = """
            INSERT INTO usuarios (nome, sobrenome, data_nascimento, genero, email, senha)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (nome, sobrenome, data_nascimento, genero, email, senha_hash))
        conn.commit()
        return jsonify({'message': 'Conta criada com sucesso!'}), 201
    except pymysql.MySQLError as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# READ ALL
@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, sobrenome, data_nascimento, genero, email FROM usuarios")
        usuarios = cursor.fetchall()
        return jsonify(usuarios), 200
    except pymysql.MySQLError as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# READ ONE BY ID
@app.route('/usuarios/<int:user_id>', methods=['GET'])
def get_usuario(user_id):
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, sobrenome, data_nascimento, genero, email FROM usuarios WHERE id=%s", (user_id,))
        usuario = cursor.fetchone()
        if usuario:
            return jsonify(usuario), 200
        return jsonify({'error': 'Usuário não encontrado'}), 404
    except pymysql.MySQLError as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# UPDATE
@app.route('/usuarios/<int:user_id>', methods=['PUT'])
def update_usuario(user_id):
    data = request.get_json()
    nome = data.get('nome')
    sobrenome = data.get('sobrenome')
    data_nascimento = data.get('data_nascimento')
    genero = data.get('genero')
    email = data.get('email')

    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        sql = """
            UPDATE usuarios
            SET nome=%s, sobrenome=%s, data_nascimento=%s, genero=%s, email=%s
            WHERE id=%s
        """
        cursor.execute(sql, (nome, sobrenome, data_nascimento, genero, email, user_id))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        return jsonify({'message': 'Usuário atualizado com sucesso!'}), 200
    except pymysql.MySQLError as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# DELETE
@app.route('/usuarios/<int:user_id>', methods=['DELETE'])
def delete_usuario(user_id):
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id=%s", (user_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        return jsonify({'message': 'Usuário deletado com sucesso!'}), 200
    except pymysql.MySQLError as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
