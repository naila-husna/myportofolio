from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Message

class MessageSerializer(serializers.ModelSerializer):
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            "id", "name", "relationship", "message", "is_anonymous",
            "created_at", "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_name(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        return value

    def validate_message(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Pesan tidak boleh kosong.")
        return value

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.is_anonymous:
            data["name"] = "Anonymous"
        return data
    
    def validate_relationship(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Relationship tidak boleh kosong.")
        return value