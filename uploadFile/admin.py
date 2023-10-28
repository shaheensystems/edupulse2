from django.contrib import admin
# from .models import UploadFile,Csv
from .models import Csv
# Register your models here.

# admin.site.register(UploadFile)

class CsvAdmin(admin.ModelAdmin):
    list_display=("id","file_name","uploaded",'activated')
admin.site.register(Csv,CsvAdmin)