# current_user variable will be available in the context for all your templates

def add_current_user_to_context(request):
    return {'current_user': request.user}