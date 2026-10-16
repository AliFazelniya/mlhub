from django.contrib import admin

from .models import MatchHistory


@admin.register(MatchHistory)
class MatchHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'board_size',
        'human_mark',
        'ai_engine',
        'human_score',
        'ai_score',
        'result',
        'created_at',
    )
    list_filter = ('board_size', 'ai_engine', 'result', 'human_mark')
    search_fields = ('result', 'ai_engine')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
