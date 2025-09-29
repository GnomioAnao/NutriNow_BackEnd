from flask import Flask, request, jsonify
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)  


db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '12345678',
    'database': 'nutrinow',
    'cursorclass': pymysql.cursors.DictCursor
}



@app.route('/', methods=['GET'])
def index():
    return 'Servidor Flask funcionando!'


@app.route('/cadastro', methods=['POST'])
def cadastro():
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

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email, senha FROM usuarios WHERE email=%s", (email,))
        usuario = cursor.fetchone()

        if usuario and check_password_hash(usuario['senha'], senha):
            return jsonify({
                'message': 'Login realizado com sucesso!',
                'usuario': {
                    'id': usuario['id'],
                    'nome': usuario['nome'],
                    'email': usuario['email']
                }
            }), 200
        else:
            return jsonify({'error': 'Email ou senha inválidos'}), 401
    except pymysql.MySQLError as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# função esqueci a senha

@app.route('/esqueci-senha', methods=['POST'])
def esqueci_senha():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'O email é obrigatório.'}), 400

    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE email=%s", (email,))
        usuario = cursor.fetchone()

        if usuario:
            return jsonify({'message': 'As instruções foram enviadas para o email.'}), 200
        else:
            return jsonify({'message': 'Email não cadastrado.'}), 404

    except pymysql.MySQLError as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


if __name__ == '__main__':
    app.run(debug=True)
