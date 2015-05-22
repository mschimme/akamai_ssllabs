from django.contrib import admin

from .models import Host
from .models import Profile
from .models import ProfileHosts
from .models import Account

class HostAdmin(admin.ModelAdmin):
    list_display = ('account_id','host','grade','endTime','supportsRC4')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('profileName','lastModified')

class ProfileHostsAdmin(admin.ModelAdmin):
    list_display = ('profileId','host')


admin.site.register(Host, HostAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(ProfileHosts, ProfileHostsAdmin)
admin.site.register(Account)