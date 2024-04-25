from django.db import models
import uuid
# from customUser.models import NewUser
# from django.contrib.auth.models import NewUser
from django.conf import settings
# Create your models here.
from django.utils import timezone
from django.contrib.auth import get_user_model
import pytz
from django.urls import reverse
from django.db.models import Count


pytz.timezone('Pacific/Auckland')

class BaseModel(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    temp_id=models.CharField(max_length=255,null=True, blank=True)
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,related_name='%(class)s_created',null=True,blank=True)
    updated_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,related_name='%(class)s_updated',null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True,verbose_name='Created At')
    updated_at=models.DateTimeField(auto_now=True,verbose_name='Updated At')
    active_status=models.BooleanField(default=True)

    class Meta:
        abstract=True
    
    def save(self, *args, **kwargs):
        if not self.pk:
            # This is a new instance, set the created_by field
            self.created_by = kwargs.pop('created_by', None)
            self.created_at=kwargs.pop('created_at',None)
          
        # Always set the updated_by and updated_at fields
        self.updated_at = timezone.now()
        # Get the logged-in user, if available
        user = kwargs.pop('updated_by', None)

        if user and isinstance(user, get_user_model()):
            # Set the updated_by field only if a valid user is provided
            self.updated_by = user
        

        super().save(*args, **kwargs)


class Address(BaseModel):
    unit_no = models.CharField(max_length=100,blank=True,null=True)
    plot_no=models.CharField(max_length=100, blank=True, null=True,)
    street=models.CharField(max_length=100, blank=True, null=True,)
    suburb=models.CharField(max_length=100, blank=True, null=True,)
    city=models.CharField(max_length=100, blank=True, null=True,)
    state=models.CharField(max_length=100, blank=True, null=True,)
    country=models.CharField(max_length=100, blank=True, null=True,)
    pin_code = models.PositiveIntegerField( blank=True, null=True,)

    def get_absolute_url(self):
      return reverse('address-detail', kwargs={'pk': self.pk})
    class Meta:
        verbose_name = "Address"  # Set the verbose name for the singular form
        verbose_name_plural = "Address"

class Campus(BaseModel):
    name=models.CharField(max_length=255,null=True,blank=True)
    address=models.ForeignKey(Address,on_delete=models.PROTECT,null=True,blank=True,related_name='campuses')

    def get_total_users(self):
        return self.users.all()
    
    def get_total_students_with_enrollment(self):
        return self.users.filter(student_profile__isnull=False)  # Count students with enrollment
    
    def get_total_students_by_gender(self):
        return self.users.values('gender').annotate(total=Count('gender'))

    def get_total_students_by_ethnicity(self):
        return self.users.values('ethnicities__name').annotate(total=Count('ethnicities__name'))

    # def calculate_total_student_enrollment(self):
    #     from report.models import StudentEnrollment
    #     student_enrollments=StudentEnrollment.objects.select_related('student').prefetch_related('student__student').filter(student__student__campus=self)
    #     return student_enrollments
    
    def calculate_total_student_enrolled(self):
        from report.models import StudentEnrollment
        from customUser.models import Student
        student_enrollments=StudentEnrollment.objects.select_related('student').prefetch_related('student__student__student_enrollments').filter(student__student__campus=self)
        enrolled_students=Student.objects.filter(student_enrollments__in=student_enrollments)
        return enrolled_students
    
    class Meta:
        verbose_name = "Campus"  # Set the verbose name for the singular form
        verbose_name_plural = "Campuses"
    
    def __str__(self):
        return f'{self.name}'