from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "token_usage" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "last_modified" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "first_created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "conversation_id" UUID NOT NULL,
    "prompt_token_usage" INT NOT NULL  DEFAULT 0,
    "completion_token_usage" INT NOT NULL  DEFAULT 0
);
COMMENT ON TABLE "token_usage" IS 'Model for tracking token usage per conversation.';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "token_usage";"""
