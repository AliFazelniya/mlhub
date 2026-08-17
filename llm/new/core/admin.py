from django.contrib import admin
from .models import QAHistory, Document
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    pass

@admin.register(QAHistory)
class QAHistoryAdmin(admin.ModelAdmin):
    list_display = ('short_query', 'status', 'llm_model', 'retrieval_latency_ms', 'created_at')
    list_filter = ('status', 'llm_model', 'created_at')
    
    readonly_fields = (
        'query_text', 'response_text', 'error_text', 
        'selected_chunk_ids', 'chunk_score_map', 
        'retrieval_latency_ms', 'llm_model', 'created_at'
    )

    def short_query(self, obj):
        if obj.query_text:
            return obj.query_text[:50] + '...' if len(obj.query_text) > 50 else obj.query_text
        return "No Query"
    short_query.short_description = 'User Query'