import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from voicebot_qc.models import Campaign, UserCampaign, CallList


class CallListTests(APITestCase):
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
        CallList.objects.create(name='call list 01', campaign=self.campaign, created_by=self.qc_lead1,
                                assign_to=self.qc_lead1)
        CallList.objects.create(name='call list 02', campaign=self.campaign, created_by=self.qc_lead1,
                                assign_to=self.qc_member1)

    def test_qc_lead_get_list_call_list(self):
        url = reverse('call_list-list', args=[self.campaign.id])
        response = self.client.get(url, HTTP_EMAIL=self.qc_lead1.email, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_json = json.loads(response.content.decode())
        self.assertEqual(len(res_json), 2)

    def test_qc_member_get_list_call_list(self):
        url = reverse('call_list-list', args=[self.campaign.id])
        response = self.client.get(url, HTTP_EMAIL=self.qc_member1.email, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_json = json.loads(response.content.decode())
        self.assertEqual(len(res_json), 1)

    def test_create_call_list_assign_user_not_permission(self):
        url = reverse('call_list-list', args=[self.campaign.id])
        data = {
            'assign_to': self.user2.email,
            'name': 'test 01'
        }
        response = self.client.post(url, data, HTTP_EMAIL=self.qc_lead1.email)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
