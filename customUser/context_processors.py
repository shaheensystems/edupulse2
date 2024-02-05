# current_user variable will be available in the context for all your templates

# def add_current_user_to_context(request):
#     return {'current_user': request.user}

# to optimized query 
from django.contrib.auth import get_user_model


def add_current_user_to_context(request):
    User = get_user_model()
    current_user = request.user
    if current_user.is_authenticated:
        # Preload related data if necessary
        related_models = set()
        for related_object in User._meta.related_objects:
            related_model = related_object.related_model
            related_models.add(related_model)

        # Convert to a list for prefetch_related
        related_models_list = list(related_models)
        # print(related_models_list)
        
        current_user = User.objects.select_related('staff_profile','student_profile','campus',)\
            .prefetch_related('groups' ).get(pk=current_user.pk)
    return {'current_user': current_user}