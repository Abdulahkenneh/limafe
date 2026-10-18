# serializers.py
from rest_framework import serializers
from .models import CustomUser

class DigitalIDSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    username = serializers.CharField()
    full_name = serializers.CharField()
    role = serializers.CharField()
    chapter = serializers.CharField(allow_null=True)
    positions = serializers.ListField(child=serializers.CharField())
    phone_number = serializers.CharField(allow_null=True)
    profile_image = serializers.CharField(allow_null=True)
    date_joined = serializers.DateTimeField(allow_null=True)

    def to_representation(self, instance):
        return instance.digital_id()
