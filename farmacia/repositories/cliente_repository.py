import sqlite3
from typing import Optional, List
from models.cliente import Cliente
from interfaces.repositories import IClienteRepository


class ClienteRepository(IClienteRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _row_para_objeto(self, row: sqlite3.Row) -> Cliente:
        return Cliente(
            id=row["id"],
            nome=row["nome"],
            telefone=row["telefone"],
            email=row["email"],
        )

    def inserir(self, cliente: Cliente) -> int:
        sql = "INSERT INTO Cliente (nome, telefone, email) VALUES (?, ?, ?)"
        cursor = self.conn.execute(sql, (cliente.nome, cliente.telefone, cliente.email))
        cliente.id = cursor.lastrowid
        return cliente.id

    def atualizar(self, cliente: Cliente) -> bool:
        sql = "UPDATE Cliente SET nome = ?, telefone = ?, email = ? WHERE id = ?"
        cursor = self.conn.execute(sql, (cliente.nome, cliente.telefone, cliente.email, cliente.id))
        return cursor.rowcount > 0

    def excluir(self, cliente_id: int) -> bool:
        sql = "DELETE FROM Cliente WHERE id = ?"
        cursor = self.conn.execute(sql, (cliente_id,))
        return cursor.rowcount > 0

    def buscar_por_id(self, cliente_id: int) -> Optional[Cliente]:
        sql = "SELECT * FROM Cliente WHERE id = ?"
        cursor = self.conn.execute(sql, (cliente_id,))
        row = cursor.fetchone()
        return self._row_para_objeto(row) if row else None

    def buscar_por_nome(self, termo: str) -> List[Cliente]:
        sql = "SELECT * FROM Cliente WHERE LOWER(nome) LIKE LOWER(?) ORDER BY nome ASC"
        cursor = self.conn.execute(sql, (f"%{termo.strip()}%",))
        return [self._row_para_objeto(row) for row in cursor.fetchall()]

    def listar_todos(self) -> List[Cliente]:
        sql = "SELECT * FROM Cliente ORDER BY nome ASC"
        cursor = self.conn.execute(sql)
        return [self._row_para_objeto(row) for row in cursor.fetchall()]

    def tem_vendas_associadas(self, cliente_id: int) -> bool:
        sql = "SELECT COUNT(*) AS total FROM Venda WHERE cliente_id = ?"
        cursor = self.conn.execute(sql, (cliente_id,))
        row = cursor.fetchone()
        return bool(row["total"] > 0) if row else False
