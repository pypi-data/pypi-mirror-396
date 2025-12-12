from django.contrib.admin.options import get_content_type_for_model

from libaudit.core import db


def set_user_audit_context(request, auth):
    """Добавляет параметры данные пользователя в контекст аудита, если аутентификация успешна."""
    if auth is None:
        return None

    user, userinfo = auth

    request._audit_context.user_id = str(user.pk)
    request._audit_context.user_type_id = get_content_type_for_model(user).id
    db.set_db_params(**request._audit_context.dict())

    return auth
