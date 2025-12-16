from datetime import datetime, timedelta, timezone, date, time
from typing import Dict, List, Optional, Callable
from ..configs.database import DatabaseManager
from ..configs.settings import db_settings
from ..configs.logging import get_logger
from typing import TypeVar
import hashlib
import uuid
import jwt
import json
from decimal import Decimal
from .templates import (
    RESOURCE_STATUS_CHANGE_HTML_TEMPLATE,
    RESOURCE_STATUS_CHANGE_TEXT_TEMPLATE,
)
import random
from ..notification import NotificationService
from ..notification import NotificationEmailServiceWriteDto

T = TypeVar("T")

logger = get_logger("helper")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class Helper:

    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """Generate a random numeric OTP of a given length."""
        return ''.join([str(random.randint(0, 9)) for _ in range(length)])

    @staticmethod
    def current_date_time():

        if 11 <= int(datetime.now().day) <= 13:
            suffix = "th"

        last_digit = int(datetime.now().day) % 10

        if last_digit == 1:
            suffix = "st"

        elif last_digit == 2:
            suffix = "nd"

        elif last_digit == 3:
            suffix = "rd"

        else:
            suffix = "th"

        now = datetime.now()
        day = now.day

        # In helper.py
        cdatetime = datetime.now().replace(microsecond=0, second=0)
        cdate = now.strftime(f"%A {day}{suffix} %B, %Y")
        ctime = now.strftime("%I:%M %p")

        return {"cdate": cdate, "ctime": ctime, "cdatetime": cdatetime}

    @staticmethod
    def generate_unique_identifier(prefix: str):

        max_length = 63
        reserved = len(prefix) + len("_")

        _uuid = f"{uuid.uuid4()}-{uuid.uuid1()}"
        hash_digest = hashlib.sha256(_uuid.encode()).hexdigest()

        return f"{prefix}_{hash_digest[:max_length - reserved]}"

    @staticmethod
    def generate_unique_resource_identifier(
        prefix: str,
        tenant_id: Optional[str],
        extra_check_functions: Optional[List[Callable[[str], Optional[int]]]] = None,
    ) -> str:
        """Generate a unique identifier that does not already exist in the resource_ids table.

        Args:
            prefix: Prefix for the identifier (e.g., 'grp', 'uid').
            tenant_id: Tenant schema name. If None, the main resource_ids table is checked.
            extra_check_functions: Optional list of callables that receive the candidate
                identifier and return a truthy value if the identifier already exists in
                another table that should be considered.

        Returns:
            A unique identifier that does not exist in the resource_ids table (and passes
            any additional uniqueness checks).
        """
        extra_checks = extra_check_functions or []

        while True:
            candidate = Helper.generate_unique_identifier(prefix=prefix)

            try:
                if tenant_id:
                    # For tenant-specific resource IDs, use CORE_PLATFORM_RESOURCE_ID_TABLE
                    # This table has tenant_id column for filtering
                    resource_table = getattr(db_settings, 'CORE_PLATFORM_RESOURCE_ID_TABLE', None)
                    if resource_table:
                        resource_exists = DatabaseManager.execute_scalar(
                            f"""SELECT COUNT(1) FROM {resource_table}
                            WHERE tenant_id = %s AND id = %s""",
                            (tenant_id, candidate,),
                        )
                    else:
                        # Fallback: assume no conflict if table not configured
                        resource_exists = 0
                else:
                    # For main/shared schema resource IDs (no tenant_id)
                    main_resource_table = getattr(db_settings, 'CORE_PLATFORM_RESOURCE_ID_TABLE', None)
                    if main_resource_table:
                        resource_exists = DatabaseManager.execute_scalar(
                            f"""SELECT COUNT(1) FROM {main_resource_table}
                            WHERE id = %s""",
                            (candidate,),
                        )
                    else:
                        # Fallback: assume no conflict if table not configured
                        resource_exists = 0
            except Exception as e:
                logger.error(
                    f"Failed to validate uniqueness for resource identifier {candidate}: {str(e)}",
                    exc_info=True,
                )
                raise

            if resource_exists and int(resource_exists or 0) > 0:
                continue

            duplicate_found = False
            for check in extra_checks:
                try:
                    result = check(candidate)
                except Exception as e:
                    logger.error(
                        f"Error while executing additional uniqueness check for {candidate}: {str(e)}",
                        exc_info=True,
                    )
                    duplicate_found = True
                    break

                if result and int(result or 0) > 0:
                    duplicate_found = True
                    break

            if duplicate_found:
                continue

            return candidate

    @staticmethod
    def map_to_dto(data: list, dto_class: T) -> List[T]:
        """
        Helper method to convert database results to DTO objects
        Args:
            data: List of database query results (dictionaries)
            dto_class: The DTO class to instantiate
        Returns:
            List of DTO instances
        """
        if not data:
            return []

        try:
            result = []
            for row in data:
                # Convert RealDictRow to regular dict
                if hasattr(row, 'items'):
                    row_dict = dict(row.items())
                else:
                    row_dict = dict(row)
                result.append(dto_class(**row_dict))
            return result
        except Exception as e:
            logger.error(f"Error mapping data to DTO: {str(e)}")
            raise

    @staticmethod
    def generate_jwt_token(data: dict, expires_delta: timedelta | None = None):

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, db_settings.SECRET_KEY, algorithm=db_settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def log_activity(
        tenant_id: str,
        action: str,
        resource_type: str,
        old_data: dict | None = None,
        new_data: dict | None = None,
        description: str | None = None,
        user_id: Optional[str] = None,
    ):
        """
        Log an activity to the activity_logs table
        Args:
            tenant_id: The tenant ID
            action: The action performed (e.g., 'create', 'update', 'delete')
            resource_type: The type of resource (e.g., 'rt-user', 'rt-group')
            old_data: The old data before the change (optional)
            new_data: The new data after the change (optional)
            description: Additional description (optional)
            user_id: The ID of the user performing the action (optional)
        """

        def serialize_for_json(obj):
            """
            Convert objects to JSON-serializable format
            """
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, date):
                return obj.isoformat()
            elif isinstance(obj, time):
                return obj.isoformat()
            elif isinstance(obj, Decimal):
                return float(obj)
            elif hasattr(obj, '__dict__'):
                # Handle custom objects by converting to dict
                return {k: serialize_for_json(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, dict):
                return {k: serialize_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [serialize_for_json(item) for item in obj]
            else:
                return obj

        try:
            # Check if table name is set
            tenant_activity_logs_table = getattr(db_settings, 'CORE_PLATFORM_ACTIVITY_LOGS_TABLE', None)
            if not tenant_activity_logs_table:
                logger.error("CORE_PLATFORM_ACTIVITY_LOGS_TABLE is not configured in settings")
                return

            log_id = Helper.generate_unique_identifier(prefix="alog")
            time_info = Helper.current_date_time()
            cdate = time_info["cdate"]
            ctime = time_info["ctime"]
            cdatetime = time_info["cdatetime"]

            # Serialize data to handle datetime and other non-JSON serializable objects
            serialized_old_data = serialize_for_json(old_data) if old_data else None
            serialized_new_data = serialize_for_json(new_data) if new_data else None

            # Convert to JSONB-compatible format
            old_json = json.dumps(serialized_old_data) if serialized_old_data else None
            new_json = json.dumps(serialized_new_data) if serialized_new_data else None

            # Fetch user information if user_id is provided
            performed_by_email = None
            performed_by_contact = None
            performed_by_fullname = None

            if user_id:
                try:
                    logger.debug(f"Fetching user information for user_id={user_id}")
                    main_users_table = getattr(db_settings, 'CORE_PLATFORM_USERS_TABLE', 'core_platform.cp_users')
                    user_data = DatabaseManager.execute_query(
                        f"""SELECT email, contact, fullname
                        FROM {main_users_table}
                        WHERE id = %s AND tenant_id = %s""",
                        (user_id, tenant_id)
                    )
                    logger.debug(f"User data query returned: {user_data}")

                    if user_data and len(user_data) > 0:
                        # RealDictRow result - all cursors now use RealDictCursor
                        user_record = user_data[0]
                        performed_by_email = user_record.get("email")
                        performed_by_contact = user_record.get("contact")
                        performed_by_fullname = user_record.get("fullname")

                        logger.debug(f"Fetched user info - email: {performed_by_email}, contact: {performed_by_contact}, fullname: {performed_by_fullname}")
                    else:
                        logger.warning(f"No user found with user_id={user_id}")
                except Exception as e:
                    logger.warning(f"Failed to fetch user information for user_id={user_id}: {str(e)}", exc_info=True)

            logger.info(f"Attempting to log activity: tenant_id={tenant_id}, action={action}, resource_type={resource_type}")
            logger.debug(f"Activity log values - performed_by_email: {performed_by_email}, performed_by_contact: {performed_by_contact}, performed_by_fullname: {performed_by_fullname}")

            result = DatabaseManager.execute_update(
                f"""INSERT INTO {tenant_activity_logs_table}
                    (id, tenant_id, action, resource_type, old_data, new_data, description, performed_by_email, performed_by_contact, performed_by_fullname, cdate, ctime, cdatetime)
                    VALUES (%s, %s, %s, NULLIF(%s, '')::text, %s::jsonb, %s::jsonb, %s, %s, %s, %s, %s, %s, %s)""",
                (log_id, tenant_id, action, resource_type, old_json, new_json, description, performed_by_email, performed_by_contact, performed_by_fullname, cdate, ctime, cdatetime),
            )

            logger.info(f"Activity logged successfully. Rows affected: {result}")

            # Verify the inserted data
            if result > 0:
                verify_data = DatabaseManager.execute_query(
                    f"""SELECT performed_by_email, performed_by_contact, performed_by_fullname
                    FROM {tenant_activity_logs_table}
                    WHERE tenant_id = %s AND id = %s""",
                    (tenant_id, log_id,)
                )
                if verify_data:
                    logger.debug(f"Verification - Inserted activity log data: {verify_data[0]}")
                else:
                    logger.warning(f"Could not verify inserted activity log with id={log_id}")

        except Exception as e:
            # Log the error but don't fail the main operation
            logger.error(f"Failed to log activity: {str(e)}", exc_info=True)

    @staticmethod
    def send_notification(
        email: str,
        subject: str,
        text_template: str,
        html_template: str,
        variables: Optional[Dict[str, str]] = None,
    ):
        """Send a dynamic notification email."""
        current_time = Helper.current_date_time()
        cdate = current_time["cdate"]
        ctime = current_time["ctime"]

        # Add defaults if not provided
        if variables is None:
            variables = {}

        # Include date/time automatically
        variables.update({"cdate": cdate, "ctime": ctime})

        def _escape(value):
            if isinstance(value, str):
                return value.replace("{", "{{").replace("}", "}}")
            return value

        safe_variables = {key: _escape(value) for key, value in variables.items()}

        # Format templates dynamically using placeholders
        text_message = text_template.format(**safe_variables)
        html_message = html_template.format(**safe_variables)

        # Build email data
        mail_sender_email = getattr(db_settings, 'MAIL_SENDER_EMAIL', None)
        mail_sender_pwd = getattr(db_settings, 'MAIL_SENDER_PWD', None)

        if not mail_sender_email or not mail_sender_pwd:
            logger.error("MAIL_SENDER_EMAIL or MAIL_SENDER_PWD not configured in settings")
            return

        notification_data = NotificationEmailServiceWriteDto(
            sender_email=mail_sender_email,
            receiver_email=email,
            password=mail_sender_pwd,
            text_message=text_message,
            html_message=html_message,
            subject=subject,
        )

        # Send email
        NotificationService.send_email(data=notification_data)

    @staticmethod
    def format_login_type_text(
        login_type: str,
        specific_days: Optional[List[str]] = None,
        custom_start: Optional[str] = None,
        custom_end: Optional[str] = None
    ) -> str:
        """
        Format login type information into human-readable text.

        Args:
            login_type: The type of login access (always_login, specific_days, custom)
            specific_days: List of days when user can login (for specific_days type)
            custom_start: Start datetime for custom login period
            custom_end: End datetime for custom login period

        Returns:
            Formatted login type description
        """
        if login_type == "always_login":
            return "Anytime - You can login at any time"
        elif login_type == "specific_days":
            if specific_days:
                days_str = ", ".join(specific_days)
                return f"Specific Days - You can login on: {days_str}"
            return "Specific Days"
        elif login_type == "custom":
            if custom_start and custom_end:
                return f"Custom Period - From {custom_start} to {custom_end}"
            elif custom_start:
                return f"Custom Period - Starting from {custom_start}"
            return "Custom Period"
        else:
            return "Login access granted"

    @staticmethod
    def get_users_with_admin_roles(tenant_id: str) -> List[Dict[str, str]]:
        """
        Get all users with role-owner or role-admin roles in a tenant.
        Checks both direct role assignments and group-based role assignments.

        Args:
            tenant_id: The tenant ID to search within

        Returns:
            List of dictionaries containing user_id, email, and name
        """
        try:
            # Get table names from settings with fallbacks
            main_users_table = getattr(db_settings, 'CORE_PLATFORM_USERS_TABLE', 'core_platform.cp_users')
            main_roles_table = getattr(db_settings, 'CORE_PLATFORM_ROLES_TABLE', 'core_platform.cp_roles')
            tenant_assign_roles_table = getattr(db_settings, 'CORE_PLATFORM_ASSIGN_ROLES_TABLE', 'core_platform.cp_assign_roles')
            tenant_user_groups_table = getattr(db_settings, 'CORE_PLATFORM_USER_GROUPS_TABLE', 'core_platform.cp_user_groups')

            # Query to get users with admin roles - both direct and through groups
            query = f"""
                SELECT DISTINCT u.id as user_id, u.email, u.fullname
                FROM {main_users_table} u
                WHERE u.tenant_id = %s
                AND u.delete_status = 'NOT_DELETED'
                AND u.is_active = true
                AND u.can_login = true
                AND (
                    -- Direct role assignment
                    (u.id, u.tenant_id) IN (
                        SELECT ar.user_id, ar.tenant_id
                        FROM {tenant_assign_roles_table} ar
                        INNER JOIN {main_roles_table} r ON ar.role_id = r.id AND ar.tenant_id = r.tenant_id
                        WHERE ar.tenant_id = %s
                        AND ar.delete_status = 'NOT_DELETED'
                        AND ar.is_active = true
                        AND r.delete_status = 'NOT_DELETED'
                        AND r.is_active = true
                        AND r.role_name IN ('role-owner', 'role-admin')
                        AND ar.user_id IS NOT NULL
                    )
                    OR
                    -- Group-based role assignment
                    (u.id, u.tenant_id) IN (
                        SELECT ug.user_id, ug.tenant_id
                        FROM {tenant_user_groups_table} ug
                        INNER JOIN {tenant_assign_roles_table} ar ON ug.group_id = ar.group_id AND ug.tenant_id = ar.tenant_id
                        INNER JOIN {main_roles_table} r ON ar.role_id = r.id AND ar.tenant_id = r.tenant_id
                        WHERE ug.tenant_id = %s
                        AND ar.tenant_id = %s
                        AND ug.delete_status = 'NOT_DELETED'
                        AND ug.is_active = true
                        AND ar.delete_status = 'NOT_DELETED'
                        AND ar.is_active = true
                        AND r.delete_status = 'NOT_DELETED'
                        AND r.is_active = true
                        AND r.role_name IN ('role-owner', 'role-admin')
                        AND ar.group_id IS NOT NULL
                    )
                )
            """

            results = DatabaseManager.execute_query(query, (tenant_id, tenant_id, tenant_id, tenant_id,))

            admin_users = []
            if results:
                for row in results:
                    row_dict = dict(row)
                    admin_users.append(
                        {
                            "user_id": row_dict.get("user_id"),
                            "email": row_dict.get("email"),
                            "name": (row_dict.get("fullname") or "").strip() or "Admin",
                        }
                    )

            logger.info(
                f"Found {len(admin_users)} admin users for tenant {tenant_id}",
                extra={"extra_fields": {"tenant_id": tenant_id, "admin_count": len(admin_users)}}
            )

            return admin_users

        except Exception as e:
            logger.error(
                f"Failed to get admin users for tenant {tenant_id}: {str(e)}",
                extra={"extra_fields": {"tenant_id": tenant_id, "error": str(e)}},
                exc_info=True
            )
            return []

    @staticmethod
    def notify_admins_of_delete_status_change(
        tenant_id: str,
        resource_type: str,
        resource_name: str,
        status: str,
        actor_user_id: Optional[str] = None,
        message: Optional[str] = None,
    ) -> None:
        """
        Notify all owner/admin users when a resource delete_status changes.

        Args:
            tenant_id: Tenant identifier
            resource_type: Human-readable resource type (e.g., "User", "Group")
            resource_name: Human-readable resource name for context
            status: New delete_status value ('PENDING', 'DELETED', 'NOT_DELETED')
            actor_user_id: User ID who performed the action
            message: Optional additional message supplied by the actor
        """
        status_key = (status or "").upper()
        status_config = {
            "PENDING": {
                "title": "Deletion Pending Approval",
                "subject": "Pending deletion request for {resource_name}",
                "description": (
                    "A deletion request has been submitted for the {resource_type} "
                    "\"{resource_name}\" and is awaiting approval."
                ),
                "display": "Pending Deletion",
                "color": "#ffc107",
                "icon": "⏳",
            },
            "DELETED": {
                "title": "Resource Deleted",
                "subject": "Resource deleted: {resource_name}",
                "description": (
                    "The {resource_type} \"{resource_name}\" has been deleted."
                ),
                "display": "Deleted",
                "color": "#dc3545",
                "icon": "🗑️",
            },
            "NOT_DELETED": {
                "title": "Resource Restored",
                "subject": "Resource restored: {resource_name}",
                "description": (
                    "The {resource_type} \"{resource_name}\" has been restored."
                ),
                "display": "Restored",
                "color": "#28a745",
                "icon": "♻️",
            },
        }

        config = status_config.get(status_key, status_config["DELETED"])

        try:
            admin_users = Helper.get_users_with_admin_roles(tenant_id)
            if not admin_users:
                logger.info(
                    "No admin users found to notify for status change",
                    extra={
                        "extra_fields": {
                            "tenant_id": tenant_id,
                            "resource_type": resource_type,
                            "resource_name": resource_name,
                            "status": status_key,
                        }
                    },
                )
                return

            actor_name = "System"
            actor_email = "no-reply@trovesuite.com"

            if actor_user_id:
                main_users_table = getattr(db_settings, 'CORE_PLATFORM_USERS_TABLE', 'core_platform.cp_users')
                actor_details = DatabaseManager.execute_query(
                    f"""SELECT fullname, email
                        FROM {main_users_table}
                        WHERE id = %s AND tenant_id = %s""",
                    (actor_user_id, tenant_id),
                )

                if actor_details and len(actor_details) > 0:
                    actor_data = dict(actor_details[0])
                    actor_name_candidate = (actor_data.get("fullname") or "").strip()
                    actor_name = actor_name_candidate or actor_data.get("email") or actor_name
                    actor_email = actor_data.get("email") or actor_email

            resource_name_display = resource_name or "Unknown resource"
            resource_type_display = resource_type or "Resource"

            message_text = f"Message: {message}\n" if message else ""
            message_row_style = "" if message else "display: none;"
            message_value = message or "No additional message provided."

            subject = config["subject"].format(
                resource_name=resource_name_display,
                resource_type=resource_type_display,
            )

            status_description = config["description"].format(
                resource_name=resource_name_display,
                resource_type=resource_type_display,
            )

            status_title = config["title"]

            app_url = getattr(db_settings, 'APP_URL', 'https://app.trovesuite.com')

            for admin in admin_users:
                admin_name = admin.get("name") or "Admin"
                Helper.send_notification(
                    email=admin["email"],
                    subject=subject,
                    text_template=RESOURCE_STATUS_CHANGE_TEXT_TEMPLATE,
                    html_template=RESOURCE_STATUS_CHANGE_HTML_TEMPLATE,
                    variables={
                        "admin_name": admin_name,
                        "resource_type": resource_type_display,
                        "resource_name": resource_name_display,
                        "status_display": config["display"],
                        "status_description": status_description,
                        "status_title": status_title,
                        "status_color": config["color"],
                        "status_icon": config["icon"],
                        "actor_name": actor_name,
                        "actor_email": actor_email,
                        "message": message_value,
                        "message_text": message_text,
                        "message_row_style": message_row_style,
                        "app_url": app_url,
                    },
                )

            logger.info(
                "Delete status change notifications sent",
                extra={
                    "extra_fields": {
                        "tenant_id": tenant_id,
                        "resource_type": resource_type_display,
                        "resource_name": resource_name_display,
                        "status": status_key,
                        "admin_count": len(admin_users),
                    }
                },
            )

        except Exception as e:
            logger.error(
                f"Failed to send delete status change notifications: {str(e)}",
                extra={
                    "extra_fields": {
                        "tenant_id": tenant_id,
                        "resource_type": resource_type,
                        "resource_name": resource_name,
                        "status": status_key,
                        "error": str(e),
                    }
                },
                exc_info=True,
            )
