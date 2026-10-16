from django import template

register = template.Library()

@register.filter
def filter_by_user_role(memberships, role):
    """Filter memberships by user role/status"""
    result = []
    for membership in memberships:
        user = membership.user
        if role == 'leader':
            if (user.role == 'admin' or
                user.positions.exists() or
                user.chapters_leadership.exists()):
                result.append(membership)
        elif role == 'regular':
            if not (user.role == 'admin' or
                   user.positions.exists() or
                   user.chapters_leadership.exists()):
                result.append(membership)
    return result