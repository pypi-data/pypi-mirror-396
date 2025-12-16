import re

import structlog
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, Group
from django.core.exceptions import SuspiciousOperation, ValidationError
from django.core.validators import validate_email
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

logger = structlog.get_logger(__name__)


class PaylaOIDCNotAuthorizedError(Exception):
    """Exception raised when a user is not authorized to access the system."""


class PaylaOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def get_username(self, claims):
        """Extract and validate username from claims."""
        email = claims.get("email", "").strip().lower()
        if not email:
            raise ValidationError("Email is required in claims")

        # Validate email format
        try:
            validate_email(email)
        except ValidationError as exc:
            raise ValidationError(f"Invalid email format: {email}") from exc

        return email

    def get_or_create_user(self, access_token, id_token, payload):
        """Returns a User instance if 1 user is found. Creates a user if not found
        and configured to do so. Returns nothing if multiple users are matched."""

        user_info = self.get_userinfo(access_token, id_token, payload)

        claims_verified = self.verify_claims(user_info)
        if not claims_verified:
            msg = "Claims verification failed"
            raise SuspiciousOperation(msg)

        # email based filtering
        users = self.filter_users_by_claims(user_info)

        if len(users) == 1:
            return self.update_user(users[0], user_info)
        if len(users) > 1:
            # In the rare case that two user accounts have the same email address,
            # bail. Randomly selecting one seems really wrong.
            msg = "Multiple users returned"
            raise SuspiciousOperation(msg)
        if (
            self.get_settings("OIDC_CREATE_USER", True)
            and Group.objects.filter(name__in=user_info.get("groups", [])).exists()
        ):
            return self.create_user(user_info)
        # When the user has no known groups for the service, we skip creation and raise an error.
        # This is to prevent unauthorized access to the system.
        logger.info(
            "Login failed: User %s has no access to the system",
            self.describe_user_by_claims(user_info),
            source="payla_oidc",
            username=self.get_username(user_info),
        )
        raise PaylaOIDCNotAuthorizedError(
            "You are not authorized to access this system. Please contact your administrator."
        )

    def authenticate(self, request, **kwargs):
        """Enhanced authentication with security checks."""
        if not request:
            return None

        try:
            user = super().authenticate(request, **kwargs)
            if user:
                logger.info("Authentication successful", source="payla_oidc", username=user.username)
        except PaylaOIDCNotAuthorizedError as e:
            logger.warning(
                "Authentication failed: %s", str(e), source="payla_oidc", username=kwargs.get("username", "unknown")
            )
            messages.error(request, str(e))
            return None
        except Exception as e:
            logger.exception("Authentication error: %s", str(e), source="payla_oidc")
            messages.error(request, "Authentication failed. Please try again.")
            return None
        else:
            return user

    def _split_name(self, name: str) -> tuple[str, str]:
        """Helper to split a full name into first and last name."""
        name = name.strip()
        if name:
            first_name, last_name = name.split(" ", 1) if " " in name else (name, "")
            return first_name.strip(), last_name.strip()
        return ("", "")

    def create_user(self, claims: dict) -> AbstractUser:
        """Return object for a newly created user account."""
        email = claims.get("email")
        username = self.get_username(claims)
        first_name, last_name = self._split_name(claims.get("name", ""))
        user = self.UserModel.objects.create_user(username, email=email, first_name=first_name, last_name=last_name)
        return self.update_user(user, claims, created=True)

    def update_user(self, user: AbstractUser, claims: dict, created: bool = False) -> AbstractUser:
        # Configurable admin group name format
        admin_group_format = getattr(settings, "PAYLA_ADMIN_GROUP_FORMAT", "coresystems-{service}-admin")
        service_name = settings.PAYLA_UTILS["MICROSERVICE_NAME"]
        admin_group = admin_group_format.format(service=service_name)
        claims_groups = set(claims.get("groups", []))
        user.is_staff = admin_group in claims_groups

        # In local development environments, make users superuser for easier testing
        if getattr(settings, 'OIDC_CREATE_SUPERUSER_IN_DEV', False):
            user.is_superuser = True
            user.is_staff = True
            logger.info(
                "User granted superuser privileges in development environment",
                source="payla_oidc",
                username=user.username,
                environment=getattr(settings, 'ENVIRONMENT', 'unknown'),
            )

        groups = set(Group.objects.filter(name__in=claims_groups))

        # Optimize group management: only add/remove as needed
        user_groups = set(user.groups.all())
        groups_to_remove = [g for g in user_groups if g.name not in claims_groups]
        groups_to_add = groups - user_groups

        for group in groups_to_remove:
            logger.info(
                "Removing user %s from group %s (not in claims)",
                user.username,
                group.name,
                source="payla_oidc",
                username=user.username,
                group=group.name,
            )
            user.groups.remove(group)

        for group in groups_to_add:
            logger.info(
                "Adding user %s to group %s (from claims)",
                user.username,
                group.name,
                source="payla_oidc",
                username=user.username,
                group=group.name,
            )
            user.groups.add(group)

        user.first_name, user.last_name = self._split_name(claims.get("name", ""))
        if not created:
            old_user = get_user_model().objects.get(id=user.id)
            if any(
                [
                    old_user.first_name != user.first_name,
                    old_user.last_name != user.last_name,
                    old_user.email != user.email,
                    old_user.is_staff != user.is_staff,
                    old_user.is_superuser != user.is_superuser,
                ]
            ):
                logger.info(
                    "Updating user %s with new claims (fields changed)",
                    user.username,
                    source="payla_oidc",
                    username=user.username,
                )
                user.save(update_fields=["first_name", "last_name", "email", "is_staff", "is_superuser"])
        else:
            user.save()
        return user

    def verify_claims(self, claims):
        """Enhanced claims verification with security checks."""
        result = True

        if not isinstance(claims, dict):
            logger.error("Claims is not a dict", source="payla_oidc")
            result = False

        # Required fields validation
        required_fields = ["email", "groups"]
        for field in required_fields:
            if field not in claims:
                logger.error("Missing required field: %s", field, source="payla_oidc")
                result = False

        # Email validation
        email = claims.get("email", "").strip()
        if not email:
            logger.error("Empty email in claims", source="payla_oidc")
            result = False
        else:
            try:
                validate_email(email)
            except ValidationError:
                logger.exception("Invalid email format in claims", source="payla_oidc")
                result = False

        # Groups validation
        groups = claims.get("groups", [])
        if not isinstance(groups, list | set):
            logger.error("Groups field must be a list or set", source="payla_oidc")
            result = False
        else:
            # Validate group names (alphanumeric, hyphens, underscores only)
            group_pattern = re.compile(r'^[a-zA-Z0-9_-]+$')
            for group in groups:
                if not isinstance(group, str) or not group_pattern.match(group):
                    logger.error("Invalid group name format: %s", group, source="payla_oidc")
                    result = False
                    break

        # Additional security checks
        if self._has_suspicious_claims(claims):
            logger.error("Suspicious claims detected", source="payla_oidc")
            result = False

        return result

    def get_userinfo(self, access_token, id_token, payload):
        """Retrieve userinfo from OIDC provider with enhanced security."""
        try:
            userinfo = super().get_userinfo(access_token, id_token, payload)

            # Sanitize userinfo for logging (remove sensitive data)
            safe_userinfo = self._sanitize_userinfo_for_logging(userinfo)
            logger.info("Fetched userinfo from OIDC provider", userinfo=safe_userinfo, source="payla_oidc")
        except Exception as e:
            logger.exception("Failed to fetch userinfo from OIDC provider", exc_info=e, source="payla_oidc")
            raise
        return userinfo

    def _sanitize_userinfo_for_logging(self, userinfo):
        """Remove sensitive information from userinfo for safe logging."""
        if not isinstance(userinfo, dict):
            return {}

        safe_info = {}
        safe_fields = ["email", "name", "groups", "sub"]

        for field in safe_fields:
            if field in userinfo:
                if field == "email":
                    # Partially mask email for privacy
                    email = userinfo[field]
                    if "@" in email:
                        local, domain = email.split("@", 1)
                        masked_local = local[:2] + "*" * (len(local) - 2) if len(local) > 2 else local  # noqa: PLR2004
                        safe_info[field] = f"{masked_local}@{domain}"
                    else:
                        safe_info[field] = "invalid_email"
                else:
                    safe_info[field] = userinfo[field]

        return safe_info

    def _has_suspicious_claims(self, claims):
        """Check for suspicious patterns in claims."""
        # Check for excessively long values
        for value in claims.values():
            if isinstance(value, str) and len(value) > 1000:  # noqa: PLR2004
                return True
            if isinstance(value, list) and len(value) > 100:  # noqa: PLR2004
                return True

        # Check for suspicious characters in email
        email = claims.get("email", "")
        return bool(any(char in email for char in ["<", ">", "script", "javascript"]))
