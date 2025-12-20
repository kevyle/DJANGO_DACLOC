from .models import Account


def current_user(request):
    """Return the Account for the logged-in session user (if any).

    Templates will get `current_user` which is an `Account` instance or None.
    This keeps your session-based auth available in templates without passing
    the object from every view.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return {'current_user': None}
    try:
        user = Account.objects.get(id=user_id)
    except Account.DoesNotExist:
        user = None
    return {'current_user': user}
