from django.contrib import admin
from django.utils.html import format_html
from .models import QAHistory, Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'progress_message', 'uploaded_at')
    list_filter = ('status', 'uploaded_at')
    
    readonly_fields = ('live_progress', 'status', 'progress_message', 'content')

    def live_progress(self, obj):
        if not obj or not obj.pk:
            return "After clicking the Save button, the processing steps will be displayed here in real-time."
        
        color = "#0d6efd" 
        if obj.status == 'completed': color = "#198754" 
        elif obj.status == 'failed': color = "#dc3545" 
        elif obj.status == 'processing': color = "#fd7e14" 

        html = f"""
        <div style="padding: 15px; background-color: #f8f9fa; border-right: 5px solid {color}; border-radius: 5px; color: #333; font-size: 14px;">
            <strong style="color: {color}; font-size: 16px;">status: {obj.get_status_display()}</strong>
            <br><br>
            <strong>Real-time report:</strong> {obj.progress_message or 'Preparing...'}
        </div>
        """
        
        if obj.status in ['pending', 'processing']:
            html += """
            <script>
                setTimeout(function(){
                    location.reload();
                }, 3000);
            </script>
            """
        return format_html(html)
    
    live_progress.short_description = "Live tracking of operations"

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