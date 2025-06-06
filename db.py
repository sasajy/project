import sqlite3
import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_PATH = "chores.db"
os.makedirs("data", exist_ok=True)

# SQLAlchemyの設定
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Chore(Base):
    __tablename__ = "chores"
    id = Column(Integer, primary_key=True)
    done_by = Column(String)  # 今は未使用。将来拡張用
    name = Column(String)
    detail = Column(String)
    mod = Column(Integer)
    amari = Column(Integer)
    done = Column(Boolean, default=False)
    date = Column(Date)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_chores_for_day(date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, detail, mod, amari, done,done_by FROM chores WHERE date = ?", (str(date),))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"name": row[0], "detail": row[1], "mod": row[2], "amari": row[3], "done": bool(row[4]),"done_by":row[5]}
        for row in rows
    ]

def save_chores_for_date(date, chore_list):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chores WHERE date = ?", (str(date),))
    for c in chore_list:
        cursor.execute("""
            INSERT INTO chores (date, name, detail, mod, amari, done, done_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (str(date), c["name"], c["detail"], c["mod"], c["amari"], c["done"], c["done_by"]))
    conn.commit()
    conn.close()

def load_all_chores_from_csv(path="chores.csv"):
    df = pd.read_csv(path)
    chores = []
    for _, row in df.iterrows():
        chores.append({
            "name": row["name"],
            "detail": row["detail"],
            "mod": int(row["mod"]),
            "amari": int(row["amari"]),
            "done": False,
            "done_by":""
        })
    return chores
