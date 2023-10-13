from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user_details" ADD "current_language_code" VARCHAR(2) NOT NULL  DEFAULT 'de';
        ALTER TABLE "user_conversations_map" ADD "language_code" VARCHAR(2) NOT NULL  DEFAULT 'de';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user_details" DROP COLUMN "current_language_code";
        ALTER TABLE "user_conversations_map" DROP COLUMN "language_code";"""
