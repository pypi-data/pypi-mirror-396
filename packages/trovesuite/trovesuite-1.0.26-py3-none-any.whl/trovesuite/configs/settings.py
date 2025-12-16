import os
class Settings:

    # Database URL
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    DB_USER: str = os.getenv("DB_USER")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_NAME: str = os.getenv("DB_NAME")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    
    # CORS Endpoint
    # LOCAL_HOST_URL = os.getenv("LOCAL_HOST_URL")
    # FRONTEND_SERVER_URL_1 = os.getenv("FRONTEND_SERVER_URL")
    # FRONTEND_SERVER_URL_2 = os.getenv("FRONTEND_SERVER_URL")

    # Application settings
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true",1)
    APP_NAME: str = os.getenv("APP_NAME", "Python Template API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "detailed")  # detailed, json, simple
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "False").lower() in ("true", 1)
    LOG_MAX_SIZE: int = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
        
   # Security settings
    ALGORITHM: str = os.getenv("ALGORITHM")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    
    # =============================================================================
    # SHARED TABLES (core_platform schema)
    # =============================================================================
    CORE_PLATFORM_TENANTS_TABLE = os.getenv("CORE_PLATFORM_TENANTS_TABLE", "core_platform.cp_tenants")
    CORE_PLATFORM_SUBSCRIPTIONS_TABLE = os.getenv("CORE_PLATFORM_SUBSCRIPTIONS_TABLE", "core_platform.cp_subscriptions")
    CORE_PLATFORM_APPS_TABLE = os.getenv("CORE_PLATFORM_APPS_TABLE", "core_platform.cp_apps")
    CORE_PLATFORM_USERS_TABLE = os.getenv("CORE_PLATFORM_USERS_TABLE", "core_platform.cp_users")
    CORE_PLATFORM_RESOURCE_TYPES_TABLE = os.getenv("CORE_PLATFORM_RESOURCE_TYPES_TABLE", "core_platform.cp_resource_types")
    CORE_PLATFORM_RESOURCE_ID_TABLE = os.getenv("CORE_PLATFORM_RESOURCE_ID_TABLE", "core_platform.cp_resource_ids")
    CORE_PLATFORM_PERMISSIONS_TABLE = os.getenv("CORE_PLATFORM_PERMISSIONS_TABLE", "core_platform.cp_permissions")
    CORE_PLATFORM_ROLES_TABLE = os.getenv("CORE_PLATFORM_ROLES_TABLE", "core_platform.cp_roles")
    CORE_PLATFORM_ROLE_PERMISSIONS_TABLE = os.getenv("CORE_PLATFORM_ROLE_PERMISSIONS_TABLE", "core_platform.cp_role_permissions")
    CORE_PLATFORM_USER_SUBSCRIPTIONS_TABLE = os.getenv("CORE_PLATFORM_USER_SUBSCRIPTIONS_TABLE", "core_platform.cp_user_subscriptions")
    CORE_PLATFORM_USER_SUBSCRIPTION_HISTORY_TABLE = os.getenv("CORE_PLATFORM_USER_SUBSCRIPTION_HISTORY_TABLE", "core_platform.cp_user_subscription_histories")
    CORE_PLATFORM_OTP = os.getenv("CORE_PLATFORM_OTP", "core_platform.cp_otps")
    CORE_PLATFORM_PASSWORD_POLICY = os.getenv("CORE_PLATFORM_PASSWORD_POLICY", "core_platform.cp_password_policies")
    CORE_PLATFORM_MULTI_FACTOR_SETTINGS = os.getenv("CORE_PLATFORM_MULTI_FACTOR_SETTINGS", "core_platform.cp_multi_factor_settings")
    CORE_PLATFORM_USER_LOGIN_TRACKING = os.getenv("CORE_PLATFORM_USER_LOGIN_TRACKING", "core_platform.cp_user_login_tracking")
    CORE_PLATFORM_ENTERPRISE_SUBSCRIPTIONS_TABLE = os.getenv("CORE_PLATFORM_ENTERPRISE_SUBSCRIPTIONS_TABLE", "core_platform.cp_enterprise_subscriptions")
    CORE_PLATFORM_CHANGE_PASSWORD_POLICY_TABLE = os.getenv("CORE_PLATFORM_CHANGE_PASSWORD_POLICY_TABLE", "core_platform.cp_change_password_policy")
    CORE_PLATFORM_APP_FEATURES_TABLE = os.getenv("CORE_PLATFORM_APP_FEATURES_TABLE", "core_platform.cp_app_features")

    # =============================================================================
    # CORE PLATFORM TABLES (prefixed with cp_, now in core_platform schema with tenant_id)
    # =============================================================================
    # NOTE: These tables have been renamed from tenant_ prefix to cp_ (core platform).
    # All tables include tenant_id column for multi-tenant isolation.
    # Tables with is_system column can contain both user and system data.
    # =============================================================================
    CORE_PLATFORM_GROUPS_TABLE = os.getenv("CORE_PLATFORM_GROUPS_TABLE", "core_platform.cp_groups")
    CORE_PLATFORM_LOGIN_SETTINGS_TABLE = os.getenv("CORE_PLATFORM_LOGIN_SETTINGS_TABLE", "core_platform.cp_login_settings")
    CORE_PLATFORM_RESOURCES_TABLE = os.getenv("CORE_PLATFORM_RESOURCES_TABLE", "core_platform.cp_resources")
    CORE_PLATFORM_ASSIGN_ROLES_TABLE = os.getenv("CORE_PLATFORM_ASSIGN_ROLES_TABLE", "core_platform.cp_assign_roles")
    CORE_PLATFORM_SUBSCRIPTION_HISTORY_TABLE = os.getenv("CORE_PLATFORM_SUBSCRIPTION_HISTORY_TABLE", "core_platform.cp_user_subscription_histories")
    CORE_PLATFORM_RESOURCE_DELETION_CHAT_HISTORY_TABLE = os.getenv("CORE_PLATFORM_RESOURCE_DELETION_CHAT_HISTORY_TABLE", "core_platform.cp_resource_deletion_chat_histories")
    CORE_PLATFORM_USER_GROUPS_TABLE = os.getenv("CORE_PLATFORM_USER_GROUPS_TABLE", "core_platform.cp_user_groups")
    CORE_PLATFORM_ACTIVITY_LOGS_TABLE = os.getenv("CORE_PLATFORM_ACTIVITY_LOGS_TABLE", "core_platform.cp_activity_logs")
    CORE_PLATFORM_ORGANIZATIONS_TABLE = os.getenv("CORE_PLATFORM_ORGANIZATIONS_TABLE", "core_platform.cp_organizations")
    CORE_PLATFORM_BUSINESSES_TABLE = os.getenv("CORE_PLATFORM_BUSINESSES_TABLE", "core_platform.cp_businesses")
    CORE_PLATFORM_BUSINESS_APPS_TABLE = os.getenv("CORE_PLATFORM_BUSINESS_APPS_TABLE", "core_platform.cp_business_apps")
    CORE_PLATFORM_LOCATIONS_TABLE = os.getenv("CORE_PLATFORM_LOCATIONS_TABLE", "core_platform.cp_locations")
    CORE_PLATFORM_ASSIGN_LOCATIONS_TABLE = os.getenv("CORE_PLATFORM_ASSIGN_LOCATIONS_TABLE", "core_platform.cp_assign_locations")
    CORE_PLATFORM_UNIT_OF_MEASURE_TABLE = os.getenv("CORE_PLATFORM_UNIT_OF_MEASURE_TABLE", "core_platform.cp_unit_of_measures")
    CORE_PLATFORM_CURRENCY = os.getenv("CORE_PLATFORM_CURRENCY", "core_platform.cp_currencies")
    CORE_PLATFORM_THEMES_TABLE = os.getenv("CORE_PLATFORM_THEMES_TABLE", "core_platform.cp_themes")

    # Mail Configurations
    MAIL_SENDER_EMAIL=os.getenv("MAIL_SENDER_EMAIL")
    MAIL_SENDER_PWD=os.getenv("MAIL_SENDER_PWD")

    # Application Configurations
    APP_URL=os.getenv("APP_URL", "https://trovesuite.com")
    USER_ASSIGNED_MANAGED_IDENTITY=os.getenv("USER_ASSIGNED_MANAGED_IDENTITY")

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        port = int(self.DB_PORT) if self.DB_PORT else 5432
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{port}/{self.DB_NAME}"

# Global settings instance
db_settings = Settings()