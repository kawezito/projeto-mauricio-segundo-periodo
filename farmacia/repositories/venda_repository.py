import sqlite3
from typing import Optional, List, Dict, Any
from models.venda import Venda
from models.item_venda import ItemVenda
from interfaces.repositories import IVendaRepository


class VendaRepository(IVendaRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def inserir_venda(self, venda: Venda) -> int:
        sql = """
            INSERT INTO Venda (cliente_id, data_venda, valor_total_centavos)
            VALUES (?, ?, ?)
        """
        cursor = self.conn.execute(
            sql,
            (venda.cliente_id, venda.data_venda, venda.valor_total_centavos),
        )
        venda.id = cursor.lastrowid
        return venda.id

    def inserir_item(self, item: ItemVenda) -> int:
        sql = """
            INSERT INTO ItemVenda (
                venda_id, medicamento_id, quantidade, preco_unitario_centavos, subtotal_centavos
            ) VALUES (?, ?, ?, ?, ?)
        """
        cursor = self.conn.execute(
            sql,
            (
                item.venda_id,
                item.medicamento_id,
                item.quantidade,
                item.preco_unitario_centavos,
                item.subtotal_centavos,
            ),
        )
        item.id = cursor.lastrowid
        return item.id

    def listar_itens_da_venda(self, venda_id: int) -> List[ItemVenda]:
        sql = """
            SELECT iv.*, m.nome AS medicamento_nome
            FROM ItemVenda iv
            JOIN Medicamento m ON m.id = iv.medicamento_id
            WHERE iv.venda_id = ?
            ORDER BY iv.id ASC
        """
        cursor = self.conn.execute(sql, (venda_id,))
        itens = []
        for row in cursor.fetchall():
            itens.append(
                ItemVenda(
                    id=row["id"],
                    venda_id=row["venda_id"],
                    medicamento_id=row["medicamento_id"],
                    medicamento_nome=row["medicamento_nome"],
                    quantidade=row["quantidade"],
                    preco_unitario_centavos=row["preco_unitario_centavos"],
                    subtotal_centavos=row["subtotal_centavos"],
                )
            )
        return itens

    def buscar_por_id(self, venda_id: int) -> Optional[Venda]:
        sql = """
            SELECT v.*, c.nome AS cliente_nome
            FROM Venda v
            LEFT JOIN Cliente c ON c.id = v.cliente_id
            WHERE v.id = ?
        """
        cursor = self.conn.execute(sql, (venda_id,))
        row = cursor.fetchone()
        if not row:
            return None
        itens = self.listar_itens_da_venda(venda_id)
        return Venda(
            id=row["id"],
            cliente_id=row["cliente_id"],
            cliente_nome=row["cliente_nome"],
            data_venda=row["data_venda"],
            valor_total_centavos=row["valor_total_centavos"],
            itens=itens,
        )

    def listar_todas(self) -> List[Venda]:
        sql = """
            SELECT v.*, c.nome AS cliente_nome
            FROM Venda v
            LEFT JOIN Cliente c ON c.id = v.cliente_id
            ORDER BY v.data_venda DESC, v.id DESC
        """
        cursor = self.conn.execute(sql)
        vendas = []
        for row in cursor.fetchall():
            itens = self.listar_itens_da_venda(row["id"])
            vendas.append(
                Venda(
                    id=row["id"],
                    cliente_id=row["cliente_id"],
                    cliente_nome=row["cliente_nome"],
                    data_venda=row["data_venda"],
                    valor_total_centavos=row["valor_total_centavos"],
                    itens=itens,
                )
            )
        return vendas

    def buscar_por_periodo(self, data_inicio: str, data_fim: str) -> List[Venda]:
        sql = """
            SELECT v.*, c.nome AS cliente_nome
            FROM Venda v
            LEFT JOIN Cliente c ON c.id = v.cliente_id
            WHERE v.data_venda >= ? AND v.data_venda <= ?
            ORDER BY v.data_venda ASC
        """
        cursor = self.conn.execute(sql, (data_inicio, data_fim))
        vendas = []
        for row in cursor.fetchall():
            itens = self.listar_itens_da_venda(row["id"])
            vendas.append(
                Venda(
                    id=row["id"],
                    cliente_id=row["cliente_id"],
                    cliente_nome=row["cliente_nome"],
                    data_venda=row["data_venda"],
                    valor_total_centavos=row["valor_total_centavos"],
                    itens=itens,
                )
            )
        return vendas

    def medicamentos_mais_vendidos(self, limite: int = 10) -> List[Dict[str, Any]]:
        sql = """
            SELECT 
                m.id AS medicamento_id,
                m.codigo,
                m.nome,
                m.categoria,
                SUM(iv.quantidade) AS total_unidades_vendidas,
                SUM(iv.subtotal_centavos) AS receita_total_centavos
            FROM ItemVenda iv
            JOIN Medicamento m ON m.id = iv.medicamento_id
            GROUP BY m.id, m.codigo, m.nome, m.categoria
            ORDER BY total_unidades_vendidas DESC
            LIMIT ?
        """
        cursor = self.conn.execute(sql, (limite,))
        return [dict(row) for row in cursor.fetchall()]

    def total_vendas_por_periodo(self, data_inicio: str, data_fim: str) -> Dict[str, Any]:
        sql = """
            SELECT 
                COUNT(*) AS total_vendas,
                COALESCE(SUM(valor_total_centavos), 0) AS valor_total_centavos
            FROM Venda
            WHERE data_venda >= ? AND data_venda <= ?
        """
        cursor = self.conn.execute(sql, (data_inicio, data_fim))
        row = cursor.fetchone()
        return dict(row) if row else {"total_vendas": 0, "valor_total_centavos": 0}
