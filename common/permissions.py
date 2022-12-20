from rest_framework import permissions

from voicebot_qc.models import Campaign, UserCampaign, CallList


class IsStaffOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff


class IsStaff(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff


class CampaignEditOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        if view.kwargs.get('pk', None):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or obj.created_by == request.user:
            return True
        try:
            user_campaign = UserCampaign.objects.get(campaign=obj, user=request.user)
            if request.method in permissions.SAFE_METHODS:
                return True
            return user_campaign.permission == UserCampaign.QC_LEAD
        except Exception:
            return False


class AdminCampaignPermission(permissions.BasePermission):
    # only OWNER or QC LEAD can action
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        campaign_id = view.kwargs.get('campaign_id', None)
        if not campaign_id:
            campaign_id = view.kwargs.get('campaign_id_pk', None)
        try:
            campaign = Campaign.objects.get(id=campaign_id)
        except Exception:
            return False
        if campaign.created_by == request.user:
            return True
        return UserCampaign.objects.filter(campaign=campaign, permission=UserCampaign.QC_LEAD,
                                           user=request.user).exists()

    def has_object_permission(self, request, view, obj):
        return True


class CallListEditOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        if view.kwargs.get('campaign_id_pk', None):
            campaign_id = view.kwargs.get('campaign_id_pk', None)
            try:
                campaign = Campaign.objects.get(id=campaign_id)
            except Exception:
                return False
            if campaign.created_by == request.user:
                return True
            return UserCampaign.objects.filter(campaign=campaign, permission=UserCampaign.QC_LEAD,
                                               user=request.user).exists()

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or obj.created_by == request.user:
            return True
        try:
            user_campaign = UserCampaign.objects.get(user=request.user, campaign__call_lists=obj)
            if request.method in permissions.SAFE_METHODS:
                return True
            return user_campaign.permission == UserCampaign.QC_LEAD
        except Exception:
            return False


class OnlyUpdateStatusCallOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        if view.kwargs.get('call_list_id_pk', None):
            call_list_id = view.kwargs.get('call_list_id_pk', None)
            try:
                call_list = CallList.objects.get(id=call_list_id)
            except Exception:
                return False
            if call_list.created_by == request.user:
                return True
            try:
                user_campaign = UserCampaign.objects.get(user=request.user, campaign=call_list.campaign)
                return user_campaign and request.method in ('PATCH', 'PUT')
            except Exception:
                return False

    def has_object_permission(self, request, view, obj):
        return True
        # if request.user.is_staff or obj.call_list.created_by == request.user:
        #     return True
        # try:
        #     user_campaign = UserCampaign.objects.get(user=request.user, campaign=obj.call_list.campaign)
        #     if request.method in permissions.SAFE_METHODS:
        #         return True
        #     return user_campaign and request.method in ('PATCH', 'PUT')
        # except Exception:
        #     return False
