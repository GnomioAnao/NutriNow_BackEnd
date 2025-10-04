from flask import Flask, request, jsonify
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS 
from datetime import datetime, timedelta
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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


def enviar_email(destinatario, assunto, mensagem_html):
    remetente = "nnutrinow@gmail.com"  
    # Rapaziada, tem que colocar a senha Flask do Google, depois vou colocar o dotenv------------------------------------------------
    senha = "Sua_senha_app_flask"    

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = destinatario
    msg.attach(MIMEText(mensagem_html, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(remetente, senha)
            server.sendmail(remetente, destinatario, msg.as_string())
        return True
    except Exception as e:
        print("Erro ao enviar email:", e)
        return False


@app.route('/esqueci-senha', methods=['POST'])
def esqueci_senha():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'O email é obrigatório.'}), 400

    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM usuarios WHERE email=%s", (email,))
        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({'message': 'Email não cadastrado.'}), 404


        token = secrets.token_urlsafe(32)
        expiracao = datetime.now() + timedelta(hours=1)


        cursor.execute("""
            INSERT INTO redefinicao_senha (usuario_id, token, data_expiracao)
            VALUES (%s, %s, %s)
        """, (usuario['id'], token, expiracao))
        conn.commit()

   
        link_reset = f"http://localhost:3000/redefinir-senha?token={token}"
        mensagem_html = f"""
        <html>
        <body>
            <h2>Redefinição de Senha - NutriNow</h2>
            <p>Olá, {usuario['nome']}!</p>
            <p>Clique no link abaixo para redefinir sua senha (válido por 1 hora):</p>
            <a href="{link_reset}" target="_blank">Redefinir minha senha</a>
            <br><br>
            <p>Se você não fez esta solicitação, ignore este e-mail.</p>
        </body>
        </html>
        """

        if enviar_email(email, "Recuperação de Senha - NutriNow", mensagem_html):
            return jsonify({'message': 'As instruções foram enviadas para o e-mail.'}), 200
        else:
            return jsonify({'error': 'Falha ao enviar o e-mail.'}), 500

    except pymysql.MySQLError as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/redefinir-senha', methods=['POST'])
def redefinir_senha():
    data = request.get_json()
    token = data.get('token')
    nova_senha = data.get('nova_senha')

    if not token or not nova_senha:
        return jsonify({'error': 'Token e nova senha são obrigatórios.'}), 400

    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT usuario_id FROM redefinicao_senha
            WHERE token=%s AND data_expiracao > NOW()
        """, (token,))
        registro = cursor.fetchone()

        if not registro:
            return jsonify({'error': 'Token inválido ou expirado.'}), 400

        senha_hash = generate_password_hash(nova_senha)
        cursor.execute("UPDATE usuarios SET senha=%s WHERE id=%s", (senha_hash, registro['usuario_id']))
        cursor.execute("DELETE FROM redefinicao_senha WHERE token=%s", (token,))
        conn.commit()

        return jsonify({'message': 'Senha redefinida com sucesso!'}), 200

    except pymysql.MySQLError as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


if __name__ == '__main__':
    app.run(debug=True)
