import docx
from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=255, verbose_name="Title")
    file = models.FileField(upload_to='documents/', verbose_name="Document File (docx)")
    content = models.TextField(blank=True, null=True, verbose_name="Extracted Content")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Uploaded At")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
        if self.file and not self.content:
            try:
                doc = docx.Document(self.file.path)
                full_text = [para.text for para in doc.paragraphs]
                self.content = '\n'.join(full_text)
                super().save(update_fields=['content'])
                
                from .vector_store import process_and_store_document
                process_and_store_document(self.id, self.content)
                
            except Exception as e:
                print(f"\n{'='*40}")
                print(f"🚨 ERROR IN DOCUMENT PROCESSING:")
                print(e)
                print(f"{'='*40}\n")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"


class QAHistory(models.Model):
    question = models.TextField(verbose_name="Question")
    answer = models.TextField(verbose_name="Answer")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    def __str__(self):
        return f"{self.question[:50]}..."

    class Meta:
        verbose_name = "QA History"
        verbose_name_plural = "QA Histories"