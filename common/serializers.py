from rest_framework import serializers
from .models import Translation

class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = [
            "id",
            "entity_type",
            "entity_id",
            "field",
            "source_lang",
            "target_lang",
            "source_text",
            "translated_text",
            "provider",
            "status",
            "checksum",
            "meta",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "translated_text",
            "status",
            "checksum",
            "meta",
            "created_at",
            "updated_at",
        ]
