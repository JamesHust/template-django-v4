from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from voicebot_qc.models import Campaign, UserCampaign


class CampaignSerializer(ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.email')
    permission = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Campaign
        fields = ["id", "name", "call_campaign_id", "created_by", "created_time", "updated_time", "permission"]
        read_only_fields = ["id", "created_by", "created_time", "updated_time"]

    def get_permission(self, obj):
        permission = ''
        user = self.context['request'].user
        if obj.created_by == user:
            permission = 'admin'
        if user.is_staff:
            permission = 'admin'
        user_campaigns = UserCampaign.objects.filter(user=user, campaign=obj)
        for user_campaign in user_campaigns:
            permission = user_campaign.permission
        return permission

    def create(self, validated_data):
        campaign = Campaign.objects.create(**validated_data)
        return campaign
