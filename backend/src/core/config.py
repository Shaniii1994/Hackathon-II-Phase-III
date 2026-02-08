from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Better Auth
    BETTER_AUTH_SECRET: str
    BETTER_AUTH_URL: str = "http://localhost:3000"

    # Database
    DATABASE_URL: str
    DATABASE_ECHO: bool = False  # Set to True for SQL query logging in development

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # JWT Settings - OWASP Compliant
    JWT_ALGORITHM: str = "HS256"
    # SECURITY: Access tokens expire in 30 minutes (OWASP recommendation: 15-30 min)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # SECURITY: Refresh tokens expire in 7 days for long-lived sessions
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Password Security - OWASP Compliant
    # SECURITY: Bcrypt rounds (work factor) - minimum 12 recommended by OWASP
    BCRYPT_ROUNDS: int = 12

    # Rate Limiting - OWASP Compliant
    # SECURITY: Maximum login attempts before rate limiting kicks in
    MAX_LOGIN_ATTEMPTS: int = 5
    # SECURITY: Rate limit window in minutes
    RATE_LIMIT_WINDOW_MINUTES: int = 15
    # SECURITY: Account lockout duration in minutes after max attempts
    ACCOUNT_LOCKOUT_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


settings = Settings()
