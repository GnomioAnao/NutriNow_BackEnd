from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from Nutri import NutritionistAgent
import mysql.connector
import os, uuid, logging
from datetime import datetime

# ---------------- Configurações ----------------
app = Flask(__name__)

# Chave secreta
app.secret_key = os.getenv("FLASK_SECRET_KEY", "uma_chave_secreta_forte_aqui")

# Configuração de cookies de sessão
app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",  # Funciona bem em localhost
    SESSION_COOKIE_SECURE=False,    # HTTPS = True, localhost = False
)

# CORS
CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}}, supports_credentials=True)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- Conexão MySQL ----------------
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', '12345678'),
        database=os.getenv('MYSQL_DATABASE', 'nutrinow2')
    )

# ---------------- Cache de agentes ----------------
agent_cache = {}
def get_agent(session_id: str, user_id: int = None, email: str = None):
    global agent_cache
    if not session_id:
        session_id = 'anon'
    key = f"{user_id}_{session_id}"
    if key in agent_cache:
        return agent_cache[key]
    logger.info(f"Criando novo NutritionistAgent para user_id={user_id}, session_id={session_id}")
    mysql_config = None
    agent = NutritionistAgent(session_id=session_id, mysql_config=mysql_config, user_id=user_id, email=email)
    agent_cache[key] = agent
    return agent

# ---------------- Rotas de autenticação ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    senha = data.get("senha")
    if not email or not senha:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, email, senha FROM usuarios WHERE email=%s", (email,))
        user = cursor.fetchone()
        if not user or not check_password_hash(user["senha"], senha):
            return jsonify({"error": "Email ou senha inválidos"}), 401

        # Cria sessão Flask
        session["user_id"] = user["id"]
        session["user_name"] = user["nome"]
        session["user_email"] = user["email"]

        return jsonify({
            "message": "Login realizado com sucesso!",
            "user": {"id": user["id"], "nome": user["nome"], "email": user["email"]}
        }), 200
    finally:
        cursor.close()
        conn.close()

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logout realizado"}), 200

# ---------------- Rotas do chatbot ----------------
@app.route("/chat", methods=["POST"])
def chat():
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401

    session_id = request.headers.get("X-Session-ID") or str(uuid.uuid4())
    user_id = session.get("user_id")
    email = session.get("user_email")
    data = request.get_json()
    message = data.get("message")
    if not message:
        return jsonify({"error": "Mensagem vazia"}), 400

    agent = get_agent(session_id=session_id, user_id=user_id, email=email)
    response_text = agent.run_text(message)
    return jsonify({"success": True, "session_id": session_id, "response": response_text}), 200

@app.route("/chat_history", methods=["GET"])
def chat_history():
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401

    session_id = request.args.get("session_id") or str(uuid.uuid4())
    user_id = session.get("user_id")
    agent = get_agent(session_id=session_id, user_id=user_id)
    history = agent.get_conversation_history(by_user=True)
    return jsonify({"success": True, "history": history})

# ---------------- Health check ----------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

# ---------------- Headers CORS extra para pré-flight ----------------
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# ---------------- Executar ----------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", 8000)), debug=True)
