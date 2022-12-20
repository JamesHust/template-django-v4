from rest_framework import viewsets

from common.common import get_campaign_with_role
from common.permissions import CallListEditOrReadOnly
from voicebot_qc.api.data_input.serializers import DataInputSerializer
from voicebot_qc.models import DataInput, UserCampaign


class DataInputViewSet(viewsets.ModelViewSet):
    serializer_class = DataInputSerializer
    permission_classes = [CallListEditOrReadOnly]

    def get_queryset(self):
        return DataInput.objects.filter(campaign__id=self.kwargs['campaign_id_pk'], campaign__is_deleted=False)

    def perform_create(self, serializer):
        campaign = get_campaign_with_role(campaign_id=self.kwargs['campaign_id_pk'], user=self.request.user,
                                          method='POST', permission=UserCampaign.QC_LEAD)

        serializer.save(campaign=campaign)
