import sqlite3
from typing import Optional, List
from models.medicamento import Medicamento
from interfaces.repositories import IMedicamentoRepository


class MedicamentoRepository(IMedicamentoRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _row_para_objeto(self, row: sqlite3.Row) -> Medicamento:
        return Medicamento(
            id=row["id"],
            codigo=row["codigo"],
            nome=row["nome"],
            fabricante=row["fabricante"],
            categoria=row["categoria"],
            apresentacao=row["apresentacao"],
            preco_centavos=row["preco_centavos"],
            estoque=row["estoque"],
            estoque_minimo=row["estoque_minimo"],
            data_validade=row["data_validade"],
        )

    def inserir(self, med: Medicamento) -> int:
        sql = """
            INSERT INTO Medicamento (
                codigo, nome, fabricante, categoria, apresentacao,
                preco_centavos, estoque, estoque_minimo, data_validade
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self.conn.execute(
            sql,
            (
                med.codigo,
                med.nome,
                med.fabricante,
                med.categoria,
                med.apresentacao,
                med.preco_centavos,
                med.estoque,
                med.estoque_minimo,
                med.data_validade,
            ),
        )
        med.id = cursor.lastrowid
        return med.id

    def atualizar(self, med: Medicamento) -> bool:
        sql = """
            UPDATE Medicamento
            SET codigo = ?, nome = ?, fabricante = ?, categoria = ?,
                apresentacao = ?, preco_centavos = ?, estoque = ?,
                estoque_minimo = ?, data_validade = ?
            WHERE id = ?
        """
        cursor = self.conn.execute(
            sql,
            (
                med.codigo,
                med.nome,
                med.fabricante,
                med.categoria,
                med.apresentacao,
                med.preco_centavos,
                med.estoque,
                med.estoque_minimo,
                med.data_validade,
                med.id,
            ),
        )
        return cursor.rowcount > 0

    def atualizar_estoque(self, medicamento_id: int, novo_estoque: int) -> bool:
        sql = "UPDATE Medicamento SET estoque = ? WHERE id = ?"
        cursor = self.conn.execute(sql, (novo_estoque, medicamento_id))
        return cursor.rowcount > 0

    def excluir(self, medicamento_id: int) -> bool:
        sql = "DELETE FROM Medicamento WHERE id = ?"
        cursor = self.conn.execute(sql, (medicamento_id,))
        return cursor.rowcount > 0

    def buscar_por_id(self, medicamento_id: int) -> Optional[Medicamento]:
        sql = "SELECT * FROM Medicamento WHERE id = ?"
        cursor = self.conn.execute(sql, (medicamento_id,))
        row = cursor.fetchone()
        return self._row_para_objeto(row) if row else None

    def buscar_por_codigo(self, codigo: str) -> Optional[Medicamento]:
        sql = "SELECT * FROM Medicamento WHERE codigo = ?"
        cursor = self.conn.execute(sql, (codigo.strip(),))
        row = cursor.fetchone()
        return self._row_para_objeto(row) if row else None

    def buscar_por_nome(self, nome_parcial: str) -> List[Medicamento]:
        sql = "SELECT * FROM Medicamento WHERE LOWER(nome) LIKE LOWER(?) ORDER BY nome ASC"
        cursor = self.conn.execute(sql, (f"%{nome_parcial.strip()}%",))
        return [self._row_para_objeto(row) for row in cursor.fetchall()]

    def listar_todos(self) -> List[Medicamento]:
        sql = "SELECT * FROM Medicamento ORDER BY nome ASC"
        cursor = self.conn.execute(sql)
        return [self._row_para_objeto(row) for row in cursor.fetchall()]

    def listar_por_categoria(self, categoria: str) -> List[Medicamento]:
        sql = "SELECT * FROM Medicamento WHERE LOWER(categoria) = LOWER(?) ORDER BY nome ASC"
        cursor = self.conn.execute(sql, (categoria.strip(),))
        return [self._row_para_objeto(row) for row in cursor.fetchall()]

    def buscar_estoque_baixo(self) -> List[Medicamento]:
        sql = "SELECT * FROM Medicamento WHERE estoque <= estoque_minimo ORDER BY estoque ASC, nome ASC"
        cursor = self.conn.execute(sql)
        return [self._row_para_objeto(row) for row in cursor.fetchall()]

    def buscar_sem_estoque(self) -> List[Medicamento]:
        sql = "SELECT * FROM Medicamento WHERE estoque = 0 ORDER BY nome ASC"
        cursor = self.conn.execute(sql)
        return [self._row_para_objeto(row) for row in cursor.fetchall()]

    def buscar_proximos_vencimento(self, data_limite: str) -> List[Medicamento]:
        sql = "SELECT * FROM Medicamento WHERE data_validade <= ? ORDER BY data_validade ASC"
        cursor = self.conn.execute(sql, (data_limite,))
        return [self._row_para_objeto(row) for row in cursor.fetchall()]

    def tem_vendas_associadas(self, medicamento_id: int) -> bool:
        sql = "SELECT COUNT(*) AS total FROM ItemVenda WHERE medicamento_id = ?"
        cursor = self.conn.execute(sql, (medicamento_id,))
        row = cursor.fetchone()
        return bool(row["total"] > 0) if row else False
