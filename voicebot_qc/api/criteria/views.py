from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from common.common import get_campaign_with_role
from common.permissions import CallListEditOrReadOnly
from voicebot_qc.api.criteria.serializers import CriteriaSerializer
from voicebot_qc.models import Criteria, UserCampaign


class CriteriaViewSet(viewsets.ModelViewSet):
    serializer_class = CriteriaSerializer
    permission_classes = [CallListEditOrReadOnly]

    def get_queryset(self):
        return Criteria.objects.filter(campaign__id=self.kwargs['campaign_id_pk'], campaign__is_deleted=False)

    def perform_create(self, serializer):
        campaign = get_campaign_with_role(campaign_id=self.kwargs['campaign_id_pk'], user=self.request.user,
                                          method='POST', permission=UserCampaign.QC_LEAD)
        data_input = self.request.data.get('data_input')
        if type(data_input) is not list:
            raise ValidationError(detail='data_input must be a list')
        serializer.save(campaign=campaign, data_input=data_input)
