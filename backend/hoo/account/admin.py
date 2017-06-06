# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Resident, Visit, Message

class ResidentAdmin(admin.ModelAdmin):
	model = Resident

class VisitAdmin(admin.ModelAdmin):
	model = Visit

class MessageAdmin(admin.ModelAdmin):
	model = Message


admin.site.register(Resident, ResidentAdmin)
admin.site.register(Visit, VisitAdmin)
admin.site.register(Message, MessageAdmin)