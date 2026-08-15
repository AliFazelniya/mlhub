from django.contrib import admin

# Register your models here.
from .models import Document, QAHistory

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')
    readonly_fields = ('content',) 

@admin.register(QAHistory)
class QAHistoryAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at')
    readonly_fields = ('question', 'answer', 'created_at')