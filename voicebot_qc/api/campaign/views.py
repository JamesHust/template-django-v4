from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet

from common.common import CampaignPagination
from voicebot_qc.api.campaign.serializers import CampaignSerializer
from voicebot_qc.models import Campaign, UserCampaign


class CampaignViewSet(ModelViewSet):
    serializer_class = CampaignSerializer
    pagination_class = CampaignPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'created_by__email', 'call_campaign_id']
    filterset_fields = ['call_campaign_id']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Campaign.objects.filter(is_deleted=False).order_by(
                self.request.query_params.get('ordering', 'name'))
        user_campaigns = UserCampaign.objects.filter(user=self.request.user)
        if self.request.query_params.get('permission'):
            user_campaigns = user_campaigns.filter(permission=self.request.query_params.get('permission'))
        queryset = Campaign.objects.filter(
            Q(id__in=[user_campaign.campaign_id for user_campaign in user_campaigns]) | Q(created_by=self.request.user),
            is_deleted=False).order_by(self.request.query_params.get('ordering', 'name'))
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
