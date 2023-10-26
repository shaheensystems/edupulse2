from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# Custom User Model
class User(AbstractUser):
    # Basic fields
    first_name = models.CharField(max_length=30, verbose_name="First Name")
    last_name = models.CharField(max_length=30, verbose_name="Last Name")
    email = models.EmailField(
        unique=True, blank=True, null=True, verbose_name="Personal Email"
    )
    is_student = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    # Optionally, if you want to use the roles and display_roles properties
    @property
    def roles(self):
        return list(self.groups.values_list("name", flat=True))

    @property
    def display_roles(self):
        return ", ".join(self.roles)


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User, related_name="student_profile", on_delete=models.CASCADE
    )
    student_id = models.IntegerField(
        blank=True, null=True, verbose_name="Student ID"
    )
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="DOB")
    student_email = models.EmailField(
        unique=True, blank=True, null=True, verbose_name="Student Email"
    )
    mobile = models.CharField(
        max_length=15, blank=True, null=True, verbose_name="Mobile"
    )
    street_address = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Address 1"
    )
    suburb = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Address 2"
    )
    city = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="City"
    )
    post_code = models.CharField(
        max_length=10, blank=True, null=True, verbose_name="Post Code"
    )
    ethnicity_1 = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Ethnicity 1"
    )
    ethnicity_2 = models.CharField(
        max_length=100, verbose_name="Ethnicity 2", blank=True, null=True
    )
    gender = models.CharField(
        max_length=10, blank=True, null=True, verbose_name="Gender"
    )
    locality = models.IntegerField(blank=True, null=True)
    is_international = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile of {self.user.first_name} {self.user.last_name}"


class StaffProfile(models.Model):
    user = models.OneToOneField(
        User, related_name="staff_profile", on_delete=models.CASCADE
    )
    staff_email = models.EmailField(
        unique=True, blank=True, null=True, verbose_name="Staff Email"
    )
    # Other staff-specific fields can be added as needed

    def __str__(self):
        return f"Profile of {self.user.first_name} {self.user.last_name}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create the StudentProfile or StaffProfile when a new User is created.
    """
    if created:
        if instance.is_student:
            StudentProfile.objects.create(user=instance)
        if instance.is_staff:
            StaffProfile.objects.create(user=instance)
