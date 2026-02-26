from sqlalchemy import text

async def seed_roles(conn):
    await conn.execute(text("""
        INSERT INTO roles (role_name) VALUES
        ('patient'),
        ('front desk assistant'),
        ('provider'),
        ('admin');
    """))