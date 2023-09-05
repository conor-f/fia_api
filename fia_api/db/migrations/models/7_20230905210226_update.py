from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "user_conversations_map" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "last_modified" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "first_created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "conversation_id" UUID NOT NULL,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "user_conversations_map" IS 'Model to simply map users to conversation IDs.';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "user_conversations_map";"""
