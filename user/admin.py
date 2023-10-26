from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import User, StudentProfile, StaffProfile


# Register your models here.
class CustomUserChangeForm(UserChangeForm):
    # personal_email = forms.EmailField()
    is_student = forms.BooleanField(required=False)

    class Meta(UserChangeForm.Meta):
        model = User


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = "Student Profile"


class StaffProfileInline(admin.StackedInline):
    model = StaffProfile
    can_delete = False
    verbose_name_plural = "Staff Profile"


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = (
        CustomUserChangeForm  # Override the default form with your custom form
    )
    inlines = (StudentProfileInline, StaffProfileInline)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_student",
        "is_staff",
    )
    list_filter = ("is_student", "is_staff")

    # Custom fieldsets to include your custom fields
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            ("Personal info"),
            {"fields": ("first_name", "last_name", "email")},
        ),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_student",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
