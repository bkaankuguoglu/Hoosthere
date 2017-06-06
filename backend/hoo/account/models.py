# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Resident(models.Model):
	username = models.CharField(blank=True, max_length=255)
	name = models.CharField(blank=True, max_length=255)
	microsoft_id = models.CharField(default='', blank=True, max_length=255)
	video_id = models.CharField(blank=True, max_length=255)
	photo_id = models.CharField(blank=True, max_length=255)

	def __str__(self):
		return self.username


class Visit(models.Model):
	visitor = models.ForeignKey(Resident, related_name = "visits", blank=False)
	date = models.DateTimeField(auto_now_add=True)
	status = models.IntegerField(default=0)
	video_id = models.CharField(blank=True, max_length=255)

	def __str__(self):
		return str(self.date)


class Message(models.Model):
	message = models.CharField(blank=True, max_length=255)
	status = models.IntegerField(default=0)
	date = models.DateTimeField(auto_now_add=True)
	target = models.ForeignKey(Resident, related_name="resident_messages", blank=False)
