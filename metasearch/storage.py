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
            actor TEXT,
            description TEXT,
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
        created = file_metadata.get("creation_time", datetime.now().isoformat())
        modified = file_metadata.get("modification_time", datetime.now().isoformat())
        extension = str(Path(file_path).suffix).lower()
        # Get annotation fields, default to empty string.
        actor = file_metadata.get("actor", "")
        description = file_metadata.get("description", "")
        # Combine content: text extracted (if any) plus annotations.
        full_text = file_metadata.get("full_text", file_metadata.get("content", ""))
        if actor:
            full_text += " " + actor
        if description:
            full_text += " " + description
        meta_json = json.dumps(file_metadata)
        query = """
        INSERT INTO files (file_path, file_name, size_bytes, created, modified, extension, actor, description, full_text, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(file_path) DO UPDATE SET
            file_name=excluded.file_name,
            size_bytes=excluded.size_bytes,
            created=excluded.created,
            modified=excluded.modified,
            extension=excluded.extension,
            actor=excluded.actor,
            description=excluded.description,
            full_text=excluded.full_text,
            metadata=excluded.metadata
        """
        self.conn.execute(query, (file_path, file_name, size, created, modified, extension, actor, description, full_text, meta_json))
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
          - key:"value"       --> key LIKE '%value%'
          - key:[X TO Y]      --> key BETWEEN X AND Y (for numeric or date fields)
        Tokens separated by AND are combined.
        If no pattern matches, default to a search in full_text.
        """
        tokens = [token.strip() for token in query_str.split("AND")]
        clauses = []
        params = []
        
        for token in tokens:
            m = re.match(r'(\w+):"([^"]+)"', token)
            if m:
                key = m.group(1)
                value = m.group(2)
                if key in ['actor', 'extension', 'file_name']:
                    clauses.append(f"{key} LIKE ?")
                    params.append(f"%{value}%")
                else:
                    clauses.append("full_text LIKE ?")
                    params.append(f"%{value}%")
                continue
            m = re.match(r'(\w+):\[(.+?)\s+TO\s*(.*?)\]', token)
            if m:
                key = m.group(1)
                start = m.group(2)
                end = m.group(3)
                # For numeric field
                if key == "size_bytes":
                    if not end:
                        clauses.append(f"{key} >= ?")
                        params.append(float(start))
                    else:
                        clauses.append(f"{key} BETWEEN ? AND ?")
                        params.append(float(start))
                        params.append(float(end))
                elif key in ['created','modified']:
                    clauses.append(f"{key} BETWEEN ? AND ?")
                    params.append(start)
                    params.append(end)
                else:
                    clauses.append("full_text LIKE ?")
                    params.append(f"%{token}%")
                continue
            # Otherwise default to searching full_text.
            clauses.append("full_text LIKE ?")
            params.append(f"%{token}%")
        
        where_clause = " AND ".join(clauses) if clauses else "1"
        return where_clause, params
    
    def search_sql(self, query_str):
        where_clause, params = self.parse_query(query_str)
        query = f"SELECT * FROM files WHERE {where_clause} LIMIT 20"
        cur = self.conn.execute(query, params)
        rows = cur.fetchall()
        return [dict(row) for row in rows]
