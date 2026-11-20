import sqlite3
from typing import List, Dict, Any
from models.movimentacao_estoque import MovimentacaoEstoque
from interfaces.repositories import IEstoqueRepository


class EstoqueRepository(IEstoqueRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def registrar_movimentacao(self, mov: MovimentacaoEstoque) -> int:
        sql = """
            INSERT INTO MovimentacaoEstoque (
                medicamento_id, tipo, quantidade, data_movimentacao, descricao
            ) VALUES (?, ?, ?, ?, ?)
        """
        cursor = self.conn.execute(
            sql,
            (
                mov.medicamento_id,
                mov.tipo,
                mov.quantidade,
                mov.data_movimentacao,
                mov.descricao,
            ),
        )
        mov.id = cursor.lastrowid
        return mov.id

    def listar_por_medicamento(self, medicamento_id: int) -> List[Dict[str, Any]]:
        sql = """
            SELECT me.*, m.nome AS medicamento_nome
            FROM MovimentacaoEstoque me
            JOIN Medicamento m ON m.id = me.medicamento_id
            WHERE me.medicamento_id = ?
            ORDER BY me.data_movimentacao DESC, me.id DESC
        """
        cursor = self.conn.execute(sql, (medicamento_id,))
        return [dict(row) for row in cursor.fetchall()]

    def listar_todas(self) -> List[Dict[str, Any]]:
        sql = """
            SELECT me.*, m.nome AS medicamento_nome
            FROM MovimentacaoEstoque me
            JOIN Medicamento m ON m.id = me.medicamento_id
            ORDER BY me.data_movimentacao DESC, me.id DESC
        """
        cursor = self.conn.execute(sql)
        return [dict(row) for row in cursor.fetchall()]
