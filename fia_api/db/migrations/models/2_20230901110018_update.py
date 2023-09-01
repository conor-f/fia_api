from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "userdetailsmodel" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "last_modified" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "first_created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "times_logged_in" INT NOT NULL  DEFAULT 0,
    "user_id_id" INT NOT NULL REFERENCES "usermodel" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "userdetailsmodel" IS 'Model for user details.';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "userdetailsmodel";"""
