from django.contrib import admin
# from .models import UploadFile,Csv
from .models import Csv,AttendanceUpload, CanvasStatsUpload,BulkAttendanceUpload
# Register your models here.

# admin.site.register(UploadFile)

class CsvAdmin(admin.ModelAdmin):
    list_display=("id","file_name","uploaded",'activated')
admin.site.register(Csv,CsvAdmin)

class AttendanceUploadAdmin(admin.ModelAdmin):
    list_display=("id","file_name","uploaded",'activated','file_path')
    def file_path(self, obj):
        return obj.file_name.path

    file_path.short_description = "File Path"
admin.site.register(AttendanceUpload,AttendanceUploadAdmin)


class CanvasStatsUploadAdmin(admin.ModelAdmin):
    list_display=("id","file_name","uploaded",'activated')
    
    


admin.site.register(CanvasStatsUpload,CanvasStatsUploadAdmin)

class BulkAttendanceUploadAdmin(admin.ModelAdmin):
    list_display=('id','file_name','time_table','uploaded','activated')
    
admin.site.register(BulkAttendanceUpload,BulkAttendanceUploadAdmin)