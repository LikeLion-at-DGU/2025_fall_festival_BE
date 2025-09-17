from django.db import models

# Create your models here.
class Translation(models.Model):
    entity_type = models.CharField(max_length=64)
    entity_id = models.CharField(max_length=64)
    field = models.CharField(max_length=64)
    source_lang = models.CharField(max_length=8)
    target_lang = models.CharField(max_length=8)
    source_text = models.TextField()
    translated_text = models.TextField(blank=True, default="")
    provider = models.CharField(max_length=16, default="google")
    status = models.CharField(max_length=16, default="pending")   # ok|stale|error|pending
    checksum = models.CharField(max_length=64)
    meta = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "translation"
        constraints = [
            models.UniqueConstraint(
                fields=["entity_type", "entity_id", "field", "target_lang"],
                name="uq_translation_target",
            )
        ]
        indexes = [
            models.Index(fields=["checksum"], name="ix_translation_checksum"),
            models.Index(fields=["status"], name="ix_translation_status"),
        ]

    def __str__(self):
        return f"{self.entity_type}:{self.entity_id}:{self.field}->{self.target_lang}"
