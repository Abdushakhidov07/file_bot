import asyncpg
from dotenv import load_dotenv
import os
load_dotenv()



async def create_db():

    pool = await asyncpg.create_pool(
        user="postgres",
        password= os.getenv("DB_PASSWORD"),
        database="bot_file",
        host="localhost",
        port=5432
    )

    await pool.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            file_id TEXT NOT NULL,
            file_type VARCHAR(20) NOT NULL,
            file_name TEXT
        )
    """)

    return pool


async def save_photo(pool, user_id, file_id):

    await pool.execute(
        """
        INSERT INTO files
        (user_id, file_id, file_type)
        VALUES ($1, $2, $3)
        """,
        user_id,
        file_id,
        "photo"
    )


async def get_photo(pool, user_id):

    return await pool.fetch(
        """
        SELECT file_id
        FROM files
        WHERE user_id = $1
        AND file_type = 'photo'
        """,
        user_id
    )


async def save_audio(pool, user_id, file_id, file_name):

    await pool.execute(
        """
        INSERT INTO files
        (user_id, file_id, file_type, file_name)
        VALUES ($1, $2, $3, $4)
        """,
        user_id,
        file_id,
        "audio",
        file_name
    )


async def get_audio(pool, user_id):

    return await pool.fetchrow(
        """
        SELECT file_id, file_name
        FROM files
        WHERE user_id = $1
        AND file_type = 'audio'
        ORDER BY id DESC
        LIMIT 1
        """,
        user_id
    )


async def get_all_files(pool, user_id):

    return await pool.fetch(
        """
        SELECT id, file_type, file_name
        FROM files
        WHERE user_id = $1
        ORDER BY id DESC
        """,
        user_id
    )
