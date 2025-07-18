import sqlite3
import os

from utils.file_utils import get_root_path

DB_PATH = f"{get_root_path()}/app/database/db.sqlite3"

def ensure_db_file_exists():
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    if not os.path.exists(DB_PATH):
        # Tạo file rỗng
        open(DB_PATH, 'a').close()

def truncate_all_tables():
    """
    Xóa data cac bảng trong database SQLite.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()

        for (table_name,) in tables:
            if table_name == "sqlite_sequence" or table_name in ["users", "roles"]:
                continue
            cur.execute(f"DELETE FROM {table_name};")
            print(f"Truncated table: {table_name}")

        conn.commit()
        print("All tables truncated successfully.")
    except sqlite3.Error as e:
        print(f"Error truncating tables: {e}")
    finally:
        conn.close() 
