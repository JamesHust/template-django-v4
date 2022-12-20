from django.contrib import admin

from voicebot_qc.models import UserCampaign, Campaign, DataInput, CallList, Call, Criteria, Record

admin.site.site_header = "Voicebot QC FPT.AI Admin"
admin.site.site_title = "Voicebot QC FPT.AI Admin Portal"
admin.site.index_title = "Welcome to Voicebot QC FPT.AI"
admin.site.disable_action('delete_selected')


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_by", "created_time", "updated_time")
    search_fields = ('created_by__email', 'name')
    list_filter = ('is_deleted', 'created_by')
    list_per_page = 20


@admin.register(CallList)
class CallListAdmin(admin.ModelAdmin):
    list_display = ("name", "campaign", "created_by", "assign_to", "status", "created_time", "updated_time")
    search_fields = ('created_by__email', 'assign_to__email', 'name')
    list_filter = ('status', 'created_by', 'assign_to')
    list_per_page = 20


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ('call_list', 'call_id', 'record_path', 'action_code', 'ending_by', 'status', 'comment')
    search_fields = ('call_list', 'call_id')
    list_filter = ('status', 'call_list__name')
    list_per_page = 20


@admin.register(Criteria)
class CriteriaAdmin(admin.ModelAdmin):
    list_display = (
        'campaign', 'name', 'description', 'is_required', 'is_monitor', 'type', 'config')
    search_fields = ('campaign', 'name')
    list_filter = ('type', 'campaign')
    list_per_page = 20


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('call', 'criteria', 'result', 'comment')
    search_fields = ('call', 'criteria')
    list_filter = ('criteria', 'call')
    list_per_page = 20


@admin.register(UserCampaign)
class UserCampaignAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'user', 'permission', 'created_time', 'created_by')
    search_fields = ('campaign', 'user', 'created_by')
    list_filter = ('campaign', 'user', 'created_by')
    list_per_page = 20


@admin.register(DataInput)
class DataInputAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'source', 'field')
    search_fields = ('campaign', 'source', 'field')
    list_filter = ('campaign', 'source', 'field')
    list_per_page = 20
