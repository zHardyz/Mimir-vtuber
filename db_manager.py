import sqlite3
import os
import json
from datetime import datetime

class ConversationDB:
    def __init__(self, db_path='conversation_history.db', max_history=100):
        """Inicializa o gerenciador de banco de dados para o histórico de conversas.
        
        Args:
            db_path (str): Caminho para o arquivo do banco de dados SQLite
            max_history (int): Número máximo de mensagens a serem mantidas no histórico
        """
        self.db_path = db_path
        self.max_history = max_history
        self._initialize_db()
    
    def _initialize_db(self):
        """Cria o banco de dados e a tabela se não existirem."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            )
            ''')
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao inicializar o banco de dados: {e}")
        finally:
            if conn:
                conn.close()
    
    def save_message(self, role, content):
        """Salva uma nova mensagem no banco de dados.
        
        Args:
            role (str): Papel da mensagem ('user' ou 'assistant')
            content (str): Conteúdo da mensagem
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            
            timestamp = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO messages (timestamp, role, content) VALUES (?, ?, ?)",
                (timestamp, role, content)
            )
            
            conn.commit()
            
            
            self._limit_history()
        except sqlite3.Error as e:
            print(f"Erro ao salvar mensagem: {e}")
        finally:
            if conn:
                conn.close()
    
    def _limit_history(self):
        """Limita o número de mensagens no histórico ao máximo definido."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
           
            cursor.execute("SELECT COUNT(*) FROM messages")
            count = cursor.fetchone()[0]
            
            
            if count > self.max_history:
                
                to_remove = count - self.max_history
                
                # Remove as mensagens mais antigas
                cursor.execute(
                    "DELETE FROM messages WHERE id IN (SELECT id FROM messages ORDER BY timestamp ASC LIMIT ?)",
                    (to_remove,)
                )
                
                conn.commit()
                print(f"Removidas {to_remove} mensagens antigas do histórico.")
        except sqlite3.Error as e:
            print(f"Erro ao limitar histórico: {e}")
        finally:
            if conn:
                conn.close()
    
    def get_recent_messages(self, limit=5):
        """Recupera as mensagens mais recentes do histórico.
        
        Args:
            limit (int): Número máximo de mensagens a serem recuperadas
            
        Returns:
            list: Lista de dicionários com as mensagens no formato {role, content}
        """
        conn = None
        messages = []
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT role, content FROM messages ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            
            rows = cursor.fetchall()
            
            # Converte as linhas em dicionários e inverte a ordem para cronológica
            messages = [{"role": row["role"], "content": row["content"]} for row in rows]
            messages.reverse()  # Inverte para ordem cronológica (mais antigas primeiro)
            
        except sqlite3.Error as e:
            print(f"Erro ao recuperar mensagens: {e}")
        finally:
            if conn:
                conn.close()
        
        return messages
    
    def clear_history(self):
        """Limpa todo o histórico de conversas."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM messages")
            conn.commit()
            
            print("Histórico de conversas limpo com sucesso.")
        except sqlite3.Error as e:
            print(f"Erro ao limpar histórico: {e}")
        finally:
            if conn:
                conn.close()