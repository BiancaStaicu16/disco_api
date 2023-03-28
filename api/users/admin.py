from django.contrib import admin
from .models import AccountTier, UserImage, User, ExpiringUserImage


admin.site.register(User)
admin.site.register(AccountTier)
admin.site.register(UserImage)
admin.site.register(ExpiringUserImage)
