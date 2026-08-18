import os
import uuid
import threading
from django.db import models
from django.utils import timezone

class Document(models.Model):
    STATUS_CHOICES = [
        ('pending', 'In the Waiting list'),
        ('processing', 'Processing (please wait)'),
        ('completed', "Processing completed successfully."),
        ('failed', 'Processing error'),
    ]

    title = models.CharField(max_length=255, verbose_name="Title")
    file = models.FileField(upload_to='documents/', verbose_name="Document File")
    content = models.TextField(blank=True, null=True, verbose_name="Extracted Content")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Uploaded At")
    
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', verbose_name="Final status")
    progress_message = models.CharField(max_length=255, blank=True, null=True, verbose_name="Current Step")

    def save(self, *args, **kwargs):
        is_new = self.pk is None 
        super().save(*args, **kwargs)

        if is_new and self.file:
            self.status = 'processing'
            self.progress_message = 'Starting processing operations...'
            super().save(update_fields=['status', 'progress_message'])
            
            thread = threading.Thread(target=self.process_document_background)
            thread.daemon = True
            thread.start()

    def process_document_background(self):
        try:
            from .document_pipeline import default_ingestor
            if not default_ingestor:
                return

            def update_progress(msg):
                self.progress_message = msg
                self.save(update_fields=['progress_message'])

            try:
                file_path = self.file.path
                with open(file_path, 'rb') as fh:
                    file_bytes = fh.read()
            except Exception:
                file_bytes = self.file.read()

            chunks = default_ingestor.ingest(
                file_bytes=file_bytes,
                filename=os.path.basename(self.file.name),
                metadata={"document_id": self.pk, "title": self.title},
                progress_callback=update_progress
            )

            if chunks and not self.content:
                self.content = "\n\n".join([c.text[:1000] for c in chunks[:3]])
            
            self.status = 'completed'
            self.progress_message = '✅ The file was successfully processed and added to the AI ​​knowledge base.'
            self.save(update_fields=['content', 'status', 'progress_message'])

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Document ingestion failed: %s", e)
            self.status = 'failed'
            self.progress_message = f"❌ Error: {str(e)}"
            self.save(update_fields=['status', 'progress_message'])

    def delete(self, *args, **kwargs):
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
                
        super().delete(*args, **kwargs)

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
