


# from pydantic_settings import BaseSettings, SettingsConfigDict


# class Settings(BaseSettings):
#     app_name: str = "Smart Document Assistant RAG"
#     app_env: str = "development"

#     gemini_api_key: str
#     gemini_embedding_model: str = "gemini-embedding-001"

#     pinecone_api_key: str
#     pinecone_index_name: str = "smart-document-assistant"

#     mongodb_uri: str
#     mongodb_db_name: str = "smart_document_assistant"

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#     )


# settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Smart Document Assistant RAG"
    app_env: str = "development"

    gemini_api_key: str
    gemini_embedding_model: str = "gemini-embedding-001"

    groq_api_key: str
    groq_model: str = "llama-3.1-8b-instant"

    pinecone_api_key: str
    pinecone_index_name: str = "smart-document-assistant-test"

    mongodb_uri: str
    mongodb_db_name: str = "smart_document_assistant"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()