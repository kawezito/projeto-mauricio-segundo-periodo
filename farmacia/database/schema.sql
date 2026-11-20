CREATE TABLE IF NOT EXISTS Medicamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    fabricante TEXT NOT NULL,
    categoria TEXT NOT NULL,
    apresentacao TEXT NOT NULL,
    preco_centavos INTEGER NOT NULL CHECK (preco_centavos >= 0),
    estoque INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0),
    estoque_minimo INTEGER NOT NULL DEFAULT 0 CHECK (estoque_minimo >= 0),
    data_validade TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Cliente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT,
    email TEXT
);

CREATE TABLE IF NOT EXISTS Venda (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    data_venda TEXT NOT NULL,
    valor_total_centavos INTEGER NOT NULL CHECK (valor_total_centavos >= 0),
    FOREIGN KEY (cliente_id) REFERENCES Cliente(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS ItemVenda (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venda_id INTEGER NOT NULL,
    medicamento_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario_centavos INTEGER NOT NULL CHECK (preco_unitario_centavos >= 0),
    subtotal_centavos INTEGER NOT NULL CHECK (subtotal_centavos >= 0),
    FOREIGN KEY (venda_id) REFERENCES Venda(id) ON DELETE CASCADE,
    FOREIGN KEY (medicamento_id) REFERENCES Medicamento(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS MovimentacaoEstoque (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicamento_id INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA')),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    data_movimentacao TEXT NOT NULL,
    descricao TEXT,
    FOREIGN KEY (medicamento_id) REFERENCES Medicamento(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_medicamento_nome ON Medicamento(nome);
CREATE INDEX IF NOT EXISTS idx_medicamento_codigo ON Medicamento(codigo);
CREATE INDEX IF NOT EXISTS idx_medicamento_categoria ON Medicamento(categoria);
CREATE INDEX IF NOT EXISTS idx_venda_data ON Venda(data_venda);
CREATE INDEX IF NOT EXISTS idx_itemvenda_venda_id ON ItemVenda(venda_id);
CREATE INDEX IF NOT EXISTS idx_itemvenda_medicamento_id ON ItemVenda(medicamento_id);
CREATE INDEX IF NOT EXISTS idx_movimentacao_medicamento_id ON MovimentacaoEstoque(medicamento_id);

