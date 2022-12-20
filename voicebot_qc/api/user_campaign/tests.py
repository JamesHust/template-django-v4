import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from voicebot_qc.models import Campaign, UserCampaign, CallList


class CampaignTests(APITestCase):
    def setUp(self):
        self.staff = User.objects.create(email='staff@fpt.com.vn', password='123', is_staff=True, username='staff')
        self.qc_lead1 = User.objects.create(email='qc_lead1@fpt.com.vn', password='123', username='qc_lead1')
        self.qc_member1 = User.objects.create(email='qc_member1@fpt.com.vn', password='123', username='qc_member1')
        self.user2 = User.objects.create(email='user2@fpt.com.vn', password='123', username='user2')
        self.campaign = Campaign.objects.create(name='test', created_by=self.staff)
        UserCampaign.objects.create(campaign=self.campaign, created_by=self.staff, user=self.qc_lead1,
                                    permission=UserCampaign.QC_LEAD)
        UserCampaign.objects.create(campaign=self.campaign, created_by=self.staff, user=self.qc_member1,
                                    permission=UserCampaign.QC_MEMBER)
        CallList.objects.create(name='test call list', campaign=self.campaign, created_by=self.qc_lead1,
                                assign_to=self.qc_lead1)

    def test_get_all_user_campaign_no_permission(self):
        url = reverse('user_campaign-list', args=[self.campaign.id])
        response = self.client.get(url, HTTP_EMAIL=self.qc_member1.email)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_all_user_campaign_have_permission(self):
        url = reverse('user_campaign-list', args=[self.campaign.id])
        response = self.client.get(url, HTTP_EMAIL=self.qc_lead1.email)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserCampaign.objects.filter(campaign=self.campaign).count(), 2)

    def test_create_user_campaign_success(self):
        url = reverse('user_campaign-list', args=[self.campaign.id])
        data = {
            "email": self.user2.email,
            "permission": UserCampaign.QC_MEMBER
        }
        response = self.client.post(url, data, format='json', HTTP_EMAIL=self.qc_lead1.email)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserCampaign.objects.filter(campaign=self.campaign).count(), 3)

    def test_create_user_campaign_email_exist(self):
        url = reverse('user_campaign-list', args=[self.campaign.id])
        data = {
            "email": self.qc_lead1.email,
            "permission": UserCampaign.QC_MEMBER
        }
        response = self.client.post(url, data, format='json', HTTP_EMAIL=self.qc_lead1.email)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UserCampaign.objects.filter(campaign=self.campaign).count(), 2)

    def test_create_user_campaign_permission_invalid(self):
        url = reverse('user_campaign-list', args=[self.campaign.id])
        data = {
            "email": self.user2.email,
            "permission": "random"
        }
        response = self.client.post(url, data, format='json', HTTP_EMAIL=self.qc_lead1.email)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UserCampaign.objects.filter(campaign=self.campaign).count(), 2)

    def test_create_user_campaign_email_not_found(self):
        url = reverse('user_campaign-list', args=[self.campaign.id])
        data = {
            "email": "random@fpt.com.vn",
            "permission": UserCampaign.QC_MEMBER
        }
        response = self.client.post(url, data, format='json', HTTP_EMAIL=self.qc_lead1.email)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(UserCampaign.objects.filter(campaign=self.campaign).count(), 2)
