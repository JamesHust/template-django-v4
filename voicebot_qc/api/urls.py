"""voicebot_qc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework_nested import routers

from voicebot_qc.api.campaign.views import CampaignViewSet
from voicebot_qc.api.user_campaign import views as user_campaign_views
from voicebot_qc.api.call_list import views as call_list_views
from voicebot_qc.api.example.views import UserViewSet
from voicebot_qc.api.data_input import views as data_input_views
from voicebot_qc.api.criteria import views as criteria_views
from voicebot_qc.api.call import views as call_views
from voicebot_qc.api.report import views as report_views

# generates:
# /campaigns/
# /campaigns/{pk}/
router = routers.SimpleRouter()
router.register(r'users', UserViewSet)
router.register(r'campaigns', CampaignViewSet, basename="campaign")

# generates:
# /campaigns/{campaign_id_pk}/users-assign/
# /campaigns/{campaign_id_pk}/users-assign/{pk}/
campaign_router = routers.NestedSimpleRouter(router, r'campaigns', lookup='campaign_id')
campaign_router.register(r'users-assign', user_campaign_views.UserCampaignViewSet, basename='user_campaign')
campaign_router.register(r'call-list', call_list_views.CallListViewSet, basename='call_list')
campaign_router.register(r'criterias', criteria_views.CriteriaViewSet, basename='criteria')
campaign_router.register(r'data-input', data_input_views.DataInputViewSet, basename='data_input')

# generates:
# /campaigns/{campaign_id_pk}/call-list/{call_list_id_pk}/calls/
# /campaigns/{campaign_id_pk}/call-list/{call_list_id_pk}/calls/{pk}/
call_list_campaign_router = routers.NestedSimpleRouter(campaign_router, r'call-list', lookup='call_list_id')
call_list_campaign_router.register(r'calls', call_views.CallViewSet, basename='call')

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"", include(campaign_router.urls)),
    path(r"", include(call_list_campaign_router.urls)),
    path('roles/', user_campaign_views.get_user_campaign_permission),
    path('campaigns/<uuid:campaign_id>/import-campaign-permission/', user_campaign_views.import_campaign_permission),
    path('campaigns/<uuid:campaign_id>/template-campaign-permission/',
         user_campaign_views.template_import_campaign_permission),

    path('campaigns/<uuid:campaign_id>/call-list/<uuid:call_list_id>/export-report-batch/',
         report_views.export_report_batch)
]
