# metasearch/storage.py

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
import re

class Storage:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_table()
    
    def _create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            file_path TEXT UNIQUE,
            file_name TEXT,
            size_bytes INTEGER,
            created DATETIME,
            modified DATETIME,
            extension TEXT,
            full_text TEXT,
            metadata TEXT
        )
        """
        self.conn.execute(query)
        self.conn.commit()
    
    def save_metadata(self, file_metadata):
        file_path = file_metadata.get("file_path")
        file_name = os.path.basename(file_path)
        size = file_metadata.get("size_bytes", 0)
        created = file_metadata.get("created", datetime.now().isoformat())
        modified = file_metadata.get("modified", datetime.now().isoformat())
        extension = str(Path(file_path).suffix).lower()
        # Build full_text: start with extracted full_text (if any), and append all annotation key-values
        base_text = file_metadata.get("full_text", file_metadata.get("content", ""))
        direct_cols = {"file_path", "file_name", "size_bytes", "created", "modified", "extension", "full_text", "metadata"}
        extra_text = ""
        for key, value in file_metadata.items():
            if key not in direct_cols:
                extra_text += f" {key}:{value}"
        full_text = base_text + extra_text
        meta_json = json.dumps(file_metadata)
        query = """
        INSERT INTO files (file_path, file_name, size_bytes, created, modified, extension, full_text, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(file_path) DO UPDATE SET
            file_name=excluded.file_name,
            size_bytes=excluded.size_bytes,
            created=excluded.created,
            modified=excluded.modified,
            extension=excluded.extension,
            full_text=excluded.full_text,
            metadata=excluded.metadata
        """
        self.conn.execute(query, (file_path, file_name, size, created, modified, extension, full_text, meta_json))
        self.conn.commit()
    
    def remove_metadata(self, file_path):
        try:
            query = "DELETE FROM files WHERE file_path = ?"
            self.conn.execute(query, (file_path,))
            self.conn.commit()
            print(f"Metadata removed for {file_path}")
        except Exception as e:
            print(f"Error removing metadata for {file_path}: {e}")
    
    def parse_query(self, query_str):
        """
        Convert a simple DSL into a SQL WHERE clause.
        Supported patterns:
          - For a token in the form key:"value" or key:value:
              If key is in our direct columns, search that column; otherwise, search in full_text using "key:value".
          - For range queries: key:[X TO Y]
          - If token doesn't match any, perform a default search in file_name and full_text.
        """
        direct_columns = {"file_name", "size_bytes", "created", "modified", "extension"}
        tokens = [t.strip() for t in query_str.split("AND")]
        clauses = []
        params = []
        for token in tokens:
            # Range query: key:[X TO Y]
            m_range = re.match(r'(\w+):\[(.+?)\s+TO\s*(.*?)\]', token)
            if m_range:
                key = m_range.group(1)
                start = m_range.group(2).strip()
                end = m_range.group(3).strip()
                if key == "size_bytes":
                    if not end:
                        clauses.append(f"{key} >= ?")
                        params.append(float(start))
                    else:
                        clauses.append(f"{key} BETWEEN ? AND ?")
                        params.append(float(start))
                        params.append(float(end))
                elif key in {"created", "modified"}:
                    clauses.append(f"{key} BETWEEN ? AND ?")
                    params.append(start)
                    params.append(end)
                else:
                    clauses.append("full_text LIKE ?")
                    params.append(f"%{token}%")
                continue
            
            # Field query with quotes: key:"value"
            m_field = re.match(r'(\w+):"([^"]+)"', token)
            if not m_field:
                m_field = re.match(r'(\w+):(\S+)', token)
            if m_field:
                key = m_field.group(1)
                value = m_field.group(2)
                if key in direct_columns:
                    clauses.append(f"{key} LIKE ?")
                    params.append(f"%{value}%")
                else:
                    # For any other key, search in full_text using the pattern "key:value"
                    clauses.append("full_text LIKE ?")
                    params.append(f"%{key}:{value}%")
                continue
            
            # Default: search in file_name and full_text.
            clauses.append("(file_name LIKE ? OR full_text LIKE ?)")
            params.append(f"%{token}%")
            params.append(f"%{token}%")
        
        where_clause = " AND ".join(clauses) if clauses else "1"
        return where_clause, params
    
    def search_sql(self, query_str):
        where_clause, params = self.parse_query(query_str)
        query = f"SELECT * FROM files WHERE {where_clause} LIMIT 20"
        cur = self.conn.execute(query, params)
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    
    def search(self, query_str):
        return self.search_sql(query_str)
