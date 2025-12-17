"""
***********************************************************************************************************************
* DISCLAIMER
* This software is supplied by Renesas Electronics Corporation and is only intended for use with Renesas products. No
* other uses are authorized. This software is owned by Renesas Electronics Corporation and is protected under all
* applicable laws, including copyright laws.
* THIS SOFTWARE IS PROVIDED "AS IS" AND RENESAS MAKES NO WARRANTIES REGARDING
* THIS SOFTWARE, WHETHER EXPRESS, IMPLIED OR STATUTORY, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. ALL SUCH WARRANTIES ARE EXPRESSLY DISCLAIMED. TO THE MAXIMUM
* EXTENT PERMITTED NOT PROHIBITED BY LAW, NEITHER RENESAS ELECTRONICS CORPORATION NOR ANY OF ITS AFFILIATED COMPANIES
* SHALL BE LIABLE FOR ANY DIRECT, INDIRECT, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES FOR ANY REASON RELATED TO THIS
* SOFTWARE, EVEN IF RENESAS OR ITS AFFILIATES HAVE BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
* Renesas reserves the right, without notice, to make changes to this software and to discontinue the availability of
* this software. By using this software, you agree to the additional terms and conditions found by accessing the
* following link:
* http://www.renesas.com/disclaimer
*
* Copyright (C) 2025 Renesas Electronics Corporation. All rights reserved.
***********************************************************************************************************************
***********************************************************************************************************************
* File Name    : history.py
* Version      : 1.01
* Product Name : AIP-CLI
* Device(s)    : N/A
* Description  : Chat History Database Management
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author  Description
* 1.00  19.11.2025  AEk     Initial revision
* 1.01  03.12.2025  AKu     Removed Punctuation Marks
***********************************************************************************************************************
"""

import pathlib
import sqlite3

# Save the DB in the user's home directory
DB_DIR = pathlib.Path.home() / ".aip"
DB_PATH = DB_DIR / "chat_history.db"


class ChatHistoryDB:
    def __init__(self):
        """
        Initialize the ChatHistoryDB class
        Parameters:
        - None
        Return:
        - None
        """
        self._init_db()

    def _init_db(self):
        """
        Initialize the database schema if it doesn't exist
        Parameters:
        - None
        Return:
        - None
        """
        if not DB_DIR.exists():
            DB_DIR.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Table for Sessions (The list you will choose from)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table for Messages (The content of the chats)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            )
        """)
        conn.commit()
        conn.close()

    def create_session(self, title: str = "New Chat") -> int | None:
        """
        Start a new chat session and return its ID
        Parameters:
        - title: The title of the session
        Return:
        - int | None: The session ID
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sessions (title) VALUES (?)", (title,))
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id

    def update_session_title(self, session_id: int, title: str):
        """
        Update the title of a session (e.g., based on the first question)
        Parameters:
        - session_id: The ID of the session to update
        - title: The new title
        Return:
        - None
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE sessions SET title = ? WHERE id = ?", (title, session_id))
        conn.commit()
        conn.close()

    def add_message(self, session_id: int, role: str, content: str):
        """
        Save a message (User or AI) to the database
        Parameters:
        - session_id: The ID of the session
        - role: The role of the message sender (e.g., 'user', 'assistant')
        - content: The message content
        Return:
        - None
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)", (session_id, role, content))
        # Update the 'updated_at' time so this session moves to the top of the list
        cursor.execute("UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (session_id,))
        conn.commit()
        conn.close()

    def get_recent_sessions(self, limit: int = 5) -> list[dict]:
        """
        Get the last N sessions for the selection menu
        Parameters:
        - limit: The maximum number of sessions to return
        Return:
        - List[Dict]: A list of session dictionaries
        """
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Allows accessing columns by name
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions ORDER BY updated_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_session_messages(self, session_id: int, limit: int = 20) -> list[dict]:
        """
        Retrieve all messages for a specific session to restore context
        Parameters:
        - session_id: The ID of the session
        - limit: The maximum number of messages to return
        Return:
        - List[Dict]: A list of message dictionaries containing 'role' and 'content'
        """
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC LIMIT ?", (session_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def delete_session(self, session_id: int) -> bool:
        """
        Delete a specific session and all associated messages
        Parameters:
        - session_id: The ID of the session to delete
        Return:
        - bool: True if deleted, False if not found
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Delete messages first (Foreign Key constraint manual cleanup)
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))

        # Delete session
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
