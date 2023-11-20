from django.contrib import admin
from base.models import Address,Campus
# Register your models here.


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id','unit_no','city', 'state', 'country','pin_code')  # Customize the displayed fields

@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display=('id','name','address')