import os
import uuid
from django.db import models
from django.utils import timezone

# Keep existing Document model but use pipeline ingestion for extraction + indexing
class Document(models.Model):
    title = models.CharField(max_length=255, verbose_name="Title")
    file = models.FileField(upload_to='documents/', verbose_name="Document File")
    content = models.TextField(blank=True, null=True, verbose_name="Extracted Content")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Uploaded At")

    def save(self, *args, **kwargs):
        # Save file first so storage path is available
        super().save(*args, **kwargs)

        # Defer heavy extraction/indexing to the document pipeline
        try:
            # Import here to avoid circular import problems during Django startup
            from .document_pipeline import default_ingestor
            if self.file and default_ingestor:
                # Read file bytes
                try:
                    file_path = self.file.path
                    with open(file_path, 'rb') as fh:
                        file_bytes = fh.read()
                except Exception:
                    # If storage backend doesn't provide path, try .read()
                    file_bytes = self.file.read()

                chunks = default_ingestor.ingest(
                    file_bytes=file_bytes,
                    filename=os.path.basename(self.file.name),
                    metadata={"document_id": self.pk, "title": self.title}
                )

                # Optionally keep a short preview in the Document.content field
                if chunks and not self.content:
                    preview = "\n\n".join([c.text[:1000] for c in chunks[:3]])
                    self.content = preview
                    super().save(update_fields=['content'])
        except Exception as e:
            # Do not raise on save failure due to ingestion; log instead
            try:
                import logging
                logger = logging.getLogger(__name__)
                logger.exception("Document.save ingestion failed: %s", e)
            except Exception:
                pass

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"


class QAHistory(models.Model):
    STATUS_CHOICES = [
        ("success", "Success"),
        ("failed", "Failed"),
        ("insufficient_info", "Insufficient Information"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    query_text = models.TextField()
    response_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Observability / Telemetry fields
    retrieval_latency_ms = models.IntegerField(null=True, blank=True, help_text="Total retrieval latency in milliseconds")
    selected_chunk_ids = models.JSONField(null=True, blank=True, help_text="List of chunk ids used for the final context")
    chunk_score_map = models.JSONField(null=True, blank=True, help_text="Map of chunk_id -> {score, rerank_score, source_doc, position}")
    llm_model = models.CharField(max_length=256, null=True, blank=True, help_text="Model name that processed the request (primary or fallback)")
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="success")
    error_text = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"QAHistory {self.id} - {self.query_text[:80]}"
