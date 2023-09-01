from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "dummymodel" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(200) NOT NULL
);
COMMENT ON TABLE "dummymodel" IS 'Model for demo purpose.';
CREATE TABLE IF NOT EXISTS "user_details" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "last_modified" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "first_created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "times_logged_in" INT NOT NULL  DEFAULT 0
);
COMMENT ON TABLE "user_details" IS 'Model for user details.';
CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "last_modified" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "first_created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "username" VARCHAR(255) NOT NULL UNIQUE,
    "password_hash" VARCHAR(255) NOT NULL,
    "is_fully_registered" BOOL NOT NULL  DEFAULT False,
    "user_details_id" INT NOT NULL UNIQUE REFERENCES "user_details" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "users" IS 'Model for users.';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
