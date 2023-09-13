from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "learning_moments" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "last_modified" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "first_created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "learning_moment" JSONB NOT NULL
);
COMMENT ON TABLE "learning_moments" IS 'Model to represent a LearningMoment.';
        CREATE TABLE IF NOT EXISTS "flashcards" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "last_modified" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "first_created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "conversation_id" UUID NOT NULL,
    "next_review_date" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "front" TEXT NOT NULL,
    "back" TEXT NOT NULL,
    "last_review_interval" INT NOT NULL  DEFAULT 60,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "flashcards" IS 'Model to represent a Flashcard.';
        CREATE TABLE "conversation_elements_learning_moments" (
    "conversation_elements_id" INT NOT NULL REFERENCES "conversation_elements" ("id") ON DELETE CASCADE,
    "learningmomentmodel_id" INT NOT NULL REFERENCES "learning_moments" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "conversation_elements_learning_moments";
        DROP TABLE IF EXISTS "learning_moments";
        DROP TABLE IF EXISTS "flashcards";"""
