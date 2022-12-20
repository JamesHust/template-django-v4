import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from voicebot_qc.api.campaign.serializers import CampaignSerializer
from voicebot_qc.models import Campaign, UserCampaign, CallList


class CampaignTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create(email='user1@fpt.com.vn', password='123', username='user1')

    def test_create_campaign(self):
        url = reverse('campaign-list')
        data = {
            'name': 'test 01',
            'call_campaign_id': "61da3f8d-04b5-4795-94ce-356f646ae8e4"
        }
        response = self.client.post(url, data, HTTP_EMAIL=self.user1.email)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(url, HTTP_EMAIL=self.user1.email)
        campaigns = Campaign.objects.filter(created_by=self.user1)
        self.assertEqual(response.data, CampaignSerializer(campaigns, many=True).data)

    # def test_get_list_campaign(self):
    #     url = reverse('campaign-list')
    #     response = self.client.get(url, HTTP_EMAIL=self.user1.email)
    #     print(response.content)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     campaigns = Campaign.objects.filter(created_by=self.user1)


class CallListTest(APITestCase):
    pass
