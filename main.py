from fastmcp import FastMCP
# from fastmcp.server.auth.providers.google import GoogleProvider
import os
import sqlite3
import json

import aiosqlite

DB_Path=os.getenv("DB_PATH",os.path.join(os.path.dirname(__file__), "expenses.db"))
CATEGORIES_path=os.path.join(os.path.dirname(__file__), "category.json")

# auth = GoogleProvider(client_id=os.getenv("GOOGLE_CLIENT_ID") or "",client_secret=os.getenv("GOOGLE_CLIENT_SECRET") or "",base_url="https://friendly-magenta-ant.fastmcp.app")
# # Create a FastMCP server instance
# mcp = FastMCP(name="Expense Tracker",auth=auth)
mcp = FastMCP(name="Expense Tracker")

def get_db_connection():
    """Get a connection to the SQLite database."""
    with sqlite3.connect(DB_Path) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            subcategory TEXT DEFAULT '',
            note TEXT DEFAULT ''
        )""")
        
get_db_connection()

@mcp.tool()
async def add_expense(date,amount,category,subcategory='',note=''):
    """Add an expense to the database."""
    async with aiosqlite.connect(DB_Path) as conn:
        cur=await conn.execute("INSERT INTO expenses (amount, category, date, subcategory, note) VALUES (?, ?, ?, ?, ?)",(amount, category, date, subcategory, note))
        await conn.commit()
        return {"status": "ok" , "id":cur.lastrowid}

@mcp.tool()
async def list_expenses(start_date,end_date):
    """List expenses between date range."""
    async with aiosqlite.connect(DB_Path) as conn:
        cur=await conn.execute("SELECT id,amount,category,date,subcategory,note FROM expenses WHERE date BETWEEN ? AND ? ORDER BY id ASC",(start_date,end_date))
        cols=[d[0] for d in cur.description]
        return [dict(zip(cols,row)) for row in await cur.fetchall()]

@mcp.tool()
async def summarize_expenses(start_date,end_date,category=None):
    """ Summarize expenses between date range by category"""
    async with aiosqlite.connect(DB_Path) as conn:
        if category:
            cur= await conn.execute("SELECT category,SUM(amount) as total from expenses where date between ? and ? and category=? group by category order by total DESC",(start_date,end_date,category))
        else:
            cur=await conn.execute("SELECT category,SUM(amount) as total from expenses where date between ? and ? group by category order by total DESC",(start_date,end_date))
        cols=[d[0] for d in cur.description]
        return [dict(zip(cols,row)) for row in await cur.fetchall()]
    
@mcp.tool()
async def edit_expense(id,amount,category,date,subcategory='',note=''):
    """Edit an existing expense."""
    async with aiosqlite.connect(DB_Path) as conn:
        await conn.execute("UPDATE expenses SET amount=?, category=?, date=?, subcategory=?, note=? WHERE id=?",(amount, category, date, subcategory, note, id))
        await conn.commit()
        return {"status": "ok", "id": id}
    
@mcp.tool()
async def delete_expense(id):
    """Delete an expense from the database."""
    async with aiosqlite.connect(DB_Path) as conn:
        await conn.execute("DELETE FROM expenses WHERE id=?",(id,))
        await conn.commit()
        return {"status": "ok", "id": id}

@mcp.resource("expense://category",mime_type="application/json")
def categories():
    """ Read the category.json file and return the categories as a JSON response."""
    with open(CATEGORIES_path, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    mcp.run()