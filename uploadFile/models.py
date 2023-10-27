from django.db import models
from base.models import BaseModel
# Create your models here.

class UploadFile(BaseModel):
    # file_name=models.CharField(max_length=255,blank=True,null=True)
    # file_path=models.CharField(max_length=255,blank=True,null=True)
    file_name = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='uploads/')

    def __str__(self):
        return self.file_name

