from django.db import models
from base.models import BaseModel
# Create your models here.

# class UploadFile(BaseModel):
#     # file_name=models.CharField(max_length=255,blank=True,null=True)
#     # file_path=models.CharField(max_length=255,blank=True,null=True)
#     file_name = models.CharField(max_length=255)
#     file_path = models.FileField(upload_to='uploads/')

#     def __str__(self):
#         return self.file_name

class Csv(models.Model):
    file_name=models.FileField(upload_to='csvs')
    uploaded=models.DateTimeField(auto_now_add=True)
    activated=models.BooleanField(default=False)

    def __str__(self):
        return f'file id:{self.id}'