from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "conversation_elements" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "last_modified" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "first_created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "conversation_id" UUID NOT NULL,
    "role" VARCHAR(9) NOT NULL,
    "content" TEXT NOT NULL
);
COMMENT ON COLUMN "conversation_elements"."role" IS 'USER: user\nSYSTEM: system\nASSISTANT: assistant';
COMMENT ON TABLE "conversation_elements" IS 'Model for a snippet of a Conversation.';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "conversation_elements";"""
