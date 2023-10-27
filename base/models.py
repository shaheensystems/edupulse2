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

pytz.timezone('Pacific/Auckland')

class BaseModel(models.Model):
    id=models.UUIDField(primary_key=True,editable=False)
    temp_id=models.CharField(max_length=255,null=True, blank=True)
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,related_name='%(class)s_created',null=True,blank=True)
    updated_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,related_name='%(class)s_updated',null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True,verbose_name='Created At')
    updated_at=models.DateTimeField(auto_now=True,verbose_name='Updated At')
    active_status=models.BooleanField()

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
    address=models.ForeignKey(Address,on_delete=models.PROTECT,null=True,blank=True)

    class Meta:
        verbose_name = "Campus"  # Set the verbose name for the singular form
        verbose_name_plural = "Campus"