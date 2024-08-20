# fetchdata/admin.py

from django.contrib import admin
from .models import Datacenter, VpsInfo, SlaveServer

@admin.register(Datacenter)
class DatacenterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(VpsInfo)
class VpsInfoAdmin(admin.ModelAdmin):
    list_display = ('vps_id', 'datacenter', 'ip', 'telegram_id', 'limit_bandwidth', 'used_bandwidth')
    search_fields = ('vps_id', 'ip', 'telegram_id')
    list_filter = ('datacenter', 'is_active')

@admin.register(SlaveServer)
class VpsInfoAdmin(admin.ModelAdmin):
    list_display = ('api_key', 'datacenter', 'api_pass', 'ip_address')
    search_fields = ('ip_address','datacenter' )
    list_filter = ('datacenter',)