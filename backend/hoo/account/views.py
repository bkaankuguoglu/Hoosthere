# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

import json
from django.http import JsonResponse
from .serializers import ResidentSerializer, VisitSerializer, MessageSerializer
from .models import Resident, Visit, Message

class register_resident(APIView):

	def post(self, request, *args, **kwargs):
		body_unicode = request.body.decode('utf-8')
		data = json.loads(body_unicode)
		username = data.get('username', '')
		name = data.get('name', '')
		microsoft_id = data.get('microsoft_id', '')
		photo_id = data.get('photo_id', '')
		video_id = data.get('video_id', '')
		resident = Resident.objects.create(username=username, name=name, microsoft_id=microsoft_id, photo_id=photo_id, video_id=video_id)

		serializer = ResidentSerializer(resident)
		return JsonResponse(serializer.data)

	def get(self, request, *args, **kwargs):
		username = request.query_params.get('username')

		resident = Resident.objects.get(username=username)
		serializer = ResidentSerializer(resident)
		return JsonResponse(serializer.data)

class update_resident(APIView):

	def post(self, request, *args, **kwargs):
		body_unicode = request.body.decode('utf-8')
		data = json.loads(body_unicode)
		username = data.get('username', '')
		name = data.get('name', '')
		microsoft_id = data.get('microsoft_id', '')
		photo_id = data.get('photo_id', '')
		video_id = data.get('video_id', '')

		resident = Resident.objects.get(username=username)
		if name != '':
			resident.name = name
		if microsoft_id != '':
			resident.microsoft_id = microsoft_id
		if photo_id != '':
			resident.photo_id = photo_id
		if video_id != '':
			resident.video_id = video_id

		resident.save()
		return JsonResponse({"result": "success"})


class create_visit(APIView):

	def post(self, request, *args, **kwargs):
		body_unicode = request.body.decode('utf-8')
		data = json.loads(body_unicode)
		username = data.get('username', '')
		video_id = data.get('video_id', '')
		status = data.get('status', 0)

		resident = Resident.objects.get(username=username)
		visit = Visit.objects.create(visitor=resident, video_id=video_id, status=status)

		serializer = VisitSerializer(visit)
		return JsonResponse(serializer.data)

	def get(self, request, *args, **kwargs):
		username = request.query_params.get('username')

		resident = Resident.objects.get(username=username)
		visit = resident.visits.filter(status=0)

		if len(visit)>0:
			serializer = VisitSerializer(visit[len(visit)-1])
			return JsonResponse(serializer.data)
		else:
			return JsonResponse({"result": "empty"})


class visit_by_id(APIView):

	def get(self, request, *args, **kwargs):
		id = request.query_params.get("id", 1)

		visit = Visit.objects.get(id=id)
		serializer = VisitSerializer(visit)
		return JsonResponse(serializer.data)


class visit_list(ListAPIView):
	serializer_class = VisitSerializer

	def get_queryset(self):
		return Visit.objects.all().order_by("-id")

class resident_list(ListAPIView):
	serializer_class = ResidentSerializer

	def get_queryset(self):
		return Resident.objects.all().order_by("name")

class microsoft_list(ListAPIView):
	serializer_class = ResidentSerializer

	def get_queryset(self):
		return Resident.objects.all().exclude(microsoft_id='').order_by("id")
		

class update_visit(APIView):

	def post(self, request, *args, **kwargs):
		body_unicode = request.body.decode('utf-8')
		data = json.loads(body_unicode)
		id = data.get("id", 0)
		status = data.get("status", 0)

		visit = Visit.objects.get(id=id)
		visit.status = status
		visit.save()
		return JsonResponse({"result": "success"})


class create_message(APIView):
	def post(self, request, *args, **kwargs):
		body_unicode = request.body.decode('utf-8')
		data = json.loads(body_unicode)

		message = data.get("message", '')
		target_username = data.get("target_username", '')

		target = Resident.objects.get(username=target_username)
		message = Message.objects.create(message=message, target=target)

		serializer = MessageSerializer(message)
		return JsonResponse(serializer.data)

	def get(self, request, *args, **kwargs):
		username = request.query_params.get('username')

		resident = Resident.objects.get(username=username)
		messages = resident.resident_messages.filter(status=0)

		if len(messages)>0:
			serializer = MessageSerializer(messages[len(messages)-1])
			return JsonResponse(serializer.data)
		else:
			return JsonResponse({"result": "empty"})

class update_message(APIView):

	def post(self, request, *args, **kwargs):
		body_unicode = request.body.decode('utf-8')
		data = json.loads(body_unicode)
		id = data.get("id", 0)
		status = data.get("status", 1)

		message = Message.objects.get(id=id)
		message.status = status
		message.save()
		return JsonResponse({"result": "success"})








