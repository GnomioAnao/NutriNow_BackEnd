CREATE database nutrinow2;

-- Banco de dados
select * from usuarios;
select * from uploads;
select * from chat_history;
select * from redefinicao_senha;
USE nutrinow2;
-- Tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    sobrenome VARCHAR(100) NOT NULL,
    data_nascimento DATE NOT NULL,
    genero ENUM('Masculino','Feminino','Não-Binário', 'Prefiro não informar') NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de redefinição de senha
CREATE TABLE IF NOT EXISTS redefinicao_senha (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    token VARCHAR(255) NOT NULL,
    data_expiracao DATETIME NOT NULL,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de histórico do chat
CREATE TABLE IF NOT EXISTS chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id INT NULL,
    email VARCHAR(255) NULL,
    message_type ENUM('human','ai') NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    INDEX idx_email (email),
    FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE uploads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    uploaded_at DATETIME NOT NULL,
    message_type ENUM('human','ai') NOT NULL DEFAULT 'human',
    FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

delete from chat_history WHERE id > 0;
ALTER TABLE chat_history AUTO_INCREMENT = 1;

DELETE FROM usuarios WHERE id > 0;
ALTER TABLE usuarios AUTO_INCREMENT = 1;

select * from perfil;
CREATE TABLE perfil (
    usuario_id INT PRIMARY KEY,
    meta VARCHAR(255) DEFAULT 'Não definida',
    altura_peso VARCHAR(50) DEFAULT '-- / --',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);