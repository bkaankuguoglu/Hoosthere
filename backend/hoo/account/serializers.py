from rest_framework import serializers
from .models import Resident, Visit, Message

class ResidentSerializer(serializers.ModelSerializer):

	class Meta:
		model = Resident
		fields = ('id', 'username', 'name', 'microsoft_id', 'video_id', 'photo_id')


class VisitSerializer(serializers.ModelSerializer):
	visitor = ResidentSerializer(many=False, read_only=True)
	date = serializers.DateTimeField(format="%H:%M %B %d, %Y")

	class Meta:
		model = Visit
		fields = ('id', 'status', 'date', 'visitor', 'video_id')


class MessageSerializer(serializers.ModelSerializer):
	target = ResidentSerializer(many=False, read_only=True)
	date = serializers.DateTimeField(format="%H:%M %B %d, %Y")

	class Meta:
		model = Message
		fields = ('id', 'status', 'date', 'message', 'target')