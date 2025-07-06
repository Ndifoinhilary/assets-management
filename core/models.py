"""
Base models for the application
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    """
    Abstract base model that provides common fields for all models
    """
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text=_("Unique identifier for the record")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at"),
        help_text=_("Date and time when the record was created")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("updated at"),
        help_text=_("Date and time when the record was last updated")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active"),
        help_text=_("Whether this record is active")
    )

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
            models.Index(fields=['is_active']),
        ]

    def soft_delete(self):
        """Soft delete the record by setting is_active to False"""
        self.is_active = False
        self.save(update_fields=['is_active'])

    def restore(self):
        """Restore a soft-deleted record"""
        self.is_active = True
        self.save(update_fields=['is_active'])