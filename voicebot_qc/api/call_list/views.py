from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.exceptions import ParseError, ValidationError, NotFound

from common.common import get_campaign_with_role, CampaignPagination
from common.permissions import CallListEditOrReadOnly
from voicebot_qc.api.call_list.serializers import CallListSerializer
from voicebot_qc.models import CallList, UserCampaign


class CallListViewSet(viewsets.ModelViewSet):
    serializer_class = CallListSerializer
    permission_classes = [CallListEditOrReadOnly]
    pagination_class = CampaignPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']

    def get_queryset(self):
        # staff/owner/qc_lead co the xem duoc tat ca call list cua campaign day, con qc_member chi xem duoc cac call list duoc assign
        call_list = CallList.objects.filter(campaign__id=self.kwargs['campaign_id_pk'], campaign__is_deleted=False)
        if self.request.user.is_staff or call_list.filter(
                campaign__user_campaigns__permission=UserCampaign.QC_LEAD,
                campaign__user_campaigns__user=self.request.user).exists():
            return call_list
        return self.request.user.assigned_call_lists.all()

    def perform_create(self, serializer):
        campaign = get_campaign_with_role(campaign_id=self.kwargs['campaign_id_pk'], user=self.request.user,
                                          method='POST', permission=UserCampaign.QC_LEAD)
        if CallList.objects.filter(campaign=campaign, name=serializer.validated_data.get('name')).exists():
            raise ParseError(detail="Name and Campaign must be unique")
        email = serializer.validated_data.get('assign_to')
        if email:
            try:
                user = User.objects.get(email=email)
                user_campaign = UserCampaign.objects.get(user=user, campaign=campaign)
                if user_campaign in user.user_user_campaigns.all():
                    assign_to = user
                else:
                    raise ValidationError(detail='Assign to non-campaign members')
            except User.DoesNotExist:
                raise NotFound(detail='Email does not exists')
            except UserCampaign.DoesNotExist:
                raise NotFound(detail='Assign to non-campaign members')
        else:
            assign_to = self.request.user
        serializer.save(
            campaign=campaign,
            created_by=self.request.user,
            assign_to=assign_to
        )
