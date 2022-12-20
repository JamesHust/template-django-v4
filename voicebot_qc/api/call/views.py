from rest_framework import viewsets

from common.common import get_call_list_or_404
from common.permissions import OnlyUpdateStatusCallOrReadOnly
from voicebot_qc.api.call.serializers import CallSerializer


class CallViewSet(viewsets.ModelViewSet):
    serializer_class = CallSerializer
    permission_classes = [OnlyUpdateStatusCallOrReadOnly]

    def get_queryset(self):
        call_list = get_call_list_or_404(campaign_id=self.kwargs['campaign_id_pk'],
                                         call_list_id=self.kwargs['call_list_id_pk'])
        return call_list.calls.all()

    def perform_create(self, serializer):
        call_list = get_call_list_or_404(campaign_id=self.kwargs['campaign_id_pk'],
                                         call_list_id=self.kwargs['call_list_id_pk'])
        serializer.save(call_list=call_list)
