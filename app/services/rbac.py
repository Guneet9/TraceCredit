from enum import Enum
from typing import Optional
from functools import wraps

from app.core.logger import get_logger

logger = get_logger(__name__)


class UserRole(str, Enum):
    CUSTOMER = "customer"
    SUPPORT = "support"
    ADMIN = "admin"


class RBACManager:
    PERMISSIONS = {
        UserRole.CUSTOMER: {
            'view_own_limit': True, 'view_own_history': True, 'view_own_explanation': True,
            'predict_limit': False, 'view_all_decisions': False,
            'manage_models': False, 'manage_users': False, 'resolve_alerts': False,
        },
        UserRole.SUPPORT: {
            'view_own_limit': True, 'view_own_history': True, 'view_own_explanation': True,
            'view_customer_history': True, 'view_customer_explanation': True,
            'predict_limit': True, 'view_all_decisions': True,
            'manage_models': False, 'manage_users': False, 'resolve_alerts': True,
        },
        UserRole.ADMIN: {
            'view_own_limit': True, 'view_own_history': True, 'view_own_explanation': True,
            'view_customer_history': True, 'view_customer_explanation': True,
            'predict_limit': True, 'view_all_decisions': True,
            'manage_models': True, 'manage_users': True, 'resolve_alerts': True,
        }
    }

    def __init__(self):
        self.active_sessions = {}

    def check_permission(self, user_role: UserRole, permission: str) -> bool:
        return self.PERMISSIONS.get(user_role, {}).get(permission, False)

    def create_session(self, user_id: int, user_role: UserRole) -> str:
        import secrets
        from datetime import datetime
        token = secrets.token_urlsafe(32)
        self.active_sessions[token] = {'user_id': user_id, 'role': user_role, 'created_at': datetime.utcnow().isoformat()}
        logger.info(f"Session created for user {user_id} (role={user_role})")
        return token

    def get_session(self, token: str) -> Optional[dict]:
        return self.active_sessions.get(token)

    def end_session(self, token: str) -> bool:
        session = self.active_sessions.pop(token, None)
        if session:
            logger.info(f"Session ended for user {session['user_id']}")
            return True
        return False

    def can_view_decision(self, user_role: UserRole, target_user_id: int, requesting_user_id: int) -> bool:
        if requesting_user_id == target_user_id:
            return True
        return self.check_permission(user_role, 'view_customer_history')

    def audit_access(self, user_id: int, user_role: UserRole, action: str, resource: str, allowed: bool):
        logger.info(f"[AUDIT] User {user_id} ({user_role}) — {action} on {resource} — {'ALLOWED' if allowed else 'DENIED'}")


def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_role = kwargs.get('user_role', UserRole.CUSTOMER)
            if not rbac_manager.check_permission(user_role, permission):
                raise PermissionError(f"Missing permission: {permission}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


rbac_manager = RBACManager()
