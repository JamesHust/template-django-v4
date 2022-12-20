import json
import re
from datetime import datetime, timezone

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.translation import gettext
from rest_framework import permissions
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from voicebot_qc.models import Campaign, UserCampaign, CallList

DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S%z"
TIME_ZONE = "+0700"
VOICE_MAIL = 'REDIRECTION_TO_NEW_DESTINATION'


def get_campaign_or_404(user, campaign_id):
    try:
        if user.is_staff:
            campaign = Campaign.objects.get(id=campaign_id, is_deleted=False)
        else:
            campaign = Campaign.objects.get(id=campaign_id, is_deleted=False)
            UserCampaign.objects.filter(user=user, campaign=campaign)
        return campaign
    except ObjectDoesNotExist:
        raise Http404


def get_call_list_or_404(campaign_id, call_list_id):
    try:
        campaign = Campaign.objects.get(id=campaign_id, is_deleted=False)
    except ObjectDoesNotExist:
        raise NotFound(detail='campaign not found')
    try:
        call_list = CallList.objects.get(id=call_list_id, status=CallList.OPEN, campaign=campaign)
    except ObjectDoesNotExist:
        raise NotFound(detail='batch not found')
    return call_list


def get_campaign_with_role(user, campaign_id, method, permission=UserCampaign.QC_MEMBER, permissions=None):
    if not permissions:
        permissions = [permission]
    try:
        campaign = Campaign.objects.get(id=campaign_id, is_deleted=False)
    except ObjectDoesNotExist:
        raise Http404

    if user.is_staff or user == campaign.created_by:
        return campaign
    if UserCampaign.objects.filter(campaign=campaign, user=user, permission__in=permissions).exists():
        return campaign
    else:
        raise PermissionDenied()


def convert_str_to_datetime(date_text):
    """
        Convert date in string format to datetime
        date_text: '2022-05-04 15:02:17+0700'
        end_time: 2022-05-04 15:02:17+07:00
    """
    try:
        return datetime.strptime(date_text, DATE_TIME_FORMAT)
    except ValueError:
        return None


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        try:
            ordering = self.request.GET['ordering']
        except KeyError as e:
            ordering = None
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'count': self.page.paginator.count,
            'ordering': ordering,
            'results': data
        })


class LargeResultsSetPagination(CustomPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


def get_list_value_from_dict(data):
    list = []
    try:
        for key, value in data.items():
            temp = [key, value]
            list.append(temp)
        list.sort()
        return [d[1] for d in list]
    except Exception as e:
        return list


def get_phone_number_standard(phone_number):
    return re.sub('^(\+84|0084)', '0', phone_number)


def get_list_value_from_mapping(mapping, data):
    list = []
    try:
        for key, value in mapping.items():
            key_temp = key
            if "||" in key:
                key_temp = key.split("||")
                key_temp = key_temp[len(key_temp) - 1]
            temp = [key, data.get(key_temp, "")]
            list.append(temp)
        list.sort()
        return [d[1] for d in list]
    except Exception as e:
        return list


def get_list_key_from_dict(data):
    list = []
    try:
        for key, value in data.items():
            temp = [key, value]
            list.append(temp)
        list.sort()
        return [d[0] for d in list]
    except Exception as e:
        return list


def get_header_from_mapping(mapping, visible_items=2):
    if not type(mapping) == dict:
        try:
            mapping = json.loads(mapping)
        except Exception as e:
            return []
    list = []
    try:
        for key, value in mapping.items():
            temp = [key, value]
            list.append(temp)
        list.sort()
    except Exception as e:
        print(e)
    result = []
    for index, item in enumerate(list):
        value = item[0]
        if "||" in value:
            value = value.split("||")
            value = value[len(value) - 1]
        result.append({'value': value, 'text': item[1], 'sortable': False, 'invisible': index > visible_items})
    return result


def get_header_from_customer_properties(properties, visible_items=2):
    list = []
    try:
        for key in properties:
            temp = [key.name, key.description, key.is_unique]
            if key.is_unique:
                list.insert(0, temp)
            else:
                list.append(temp)
        list.sort()
    except Exception as e:
        print(e)
    result = []
    for index, item in enumerate(list):
        result.append({'value': item[0], 'text': item[1], 'is_unique': item[2], 'sortable': False,
                       'invisible': index > visible_items})
    return result


def get_headers_data_call(campaign: Campaign):
    customer_properties = [
        {'value': 'phone_number', 'text': 'Telephone', 'sortable': False, 'invisible': False},
        {'value': 'name', 'text': 'Name', 'sortable': False, 'invisible': False}
        # {'value': 'custom_unique_id', 'text': 'Unique Id', 'sortable': False, 'invisible': False}
    ]
    for property in campaign.customer_properties.all():
        if property.is_unique:
            customer_properties.append(
                {'value': property.name, 'text': property.description, 'sortable': False, 'invisible': False})
        else:
            customer_properties.append(
                {'value': property.name, 'text': property.description, 'sortable': False, 'invisible': True})
    return [
        {'value': 'customer', 'text': 'Customer Info',
         'children': customer_properties},
        {'value': 'calling_info', 'text': 'Calling Info',
         'children': [
             {'value': 'id', 'text': 'Call ID', 'sortable': False, 'invisible': True},
             {'value': 'start_time', 'text': 'Start time', 'sortable': False, 'invisible': False},
             {'value': 'pickup_time', 'text': 'Pickup time', 'sortable': False, 'invisible': False},
             {'value': 'end_time', 'text': 'End time', 'sortable': False, 'invisible': True},
             {'value': 'duration', 'text': 'Duration', 'sortable': False, 'invisible': False},
             {'value': 'status', 'text': 'Status', 'sortable': False, 'invisible': False},
             {'value': 'service_number', 'text': 'Service Number', 'sortable': False, 'invisible': True},
             {'value': 'action_code', 'text': 'Action Code', 'sortable': False, 'invisible': True},
             {'value': 'voice', 'text': 'Voice', 'sortable': False, 'invisible': True},
             {'value': 'call_transfer_duration', 'text': 'Call transfer duration', 'sortable': False,
              'invisible': True},
             {'value': 'record_url', 'text': 'Record', 'sortable': False, 'invisible': False},
             {'value': 'record_path', 'text': 'Record Path', 'sortable': False, 'invisible': True},
             {'value': 'bridge', 'text': 'Forwarded Call', 'sortable': False, 'invisible': True},
             {'value': 'end_cause', 'text': 'Ending call by', 'sortable': False, 'invisible': True}
         ]
         },
        {'value': 'data_collection', 'text': 'Data collection',
         'children': get_header_from_mapping(campaign.data_collection_mapping)}
    ]


def get_customer_headers(attributes):
    return [
        {'value': 'customer_info', 'text': 'Customer Info',
         'children': [
             {'value': 'id', 'text': 'Id', 'sortable': False, 'invisible': True},
             {'value': 'phone_number', 'text': gettext('Telephone'), 'sortable': False, 'invisible': False},
             {'value': 'name', 'text': gettext('Name'), 'sortable': True, 'invisible': False},
             {'value': 'status', 'text': gettext('Status'), 'sortable': True, 'invisible': False}
         ]},
        {'value': 'general_info', 'text': gettext('General Info'),
         'children': get_header_from_customer_properties(attributes, 10)}
    ]


def get_headers_data_overview():
    return [
        {'value': 'title', 'text': gettext('Campaigns'), 'sortable': False, 'invisible': False},
        {'value': 'status', 'text': gettext('Status'), 'sortable': False, 'invisible': False},
        {'value': 'total_call', 'text': gettext('Total Calls'), 'sortable': False, 'invisible': False},
        {'value': 'connected_call', 'text': gettext('Connected Calls'), 'sortable': False, 'invisible': False},
        {'value': 'total_call_time', 'text': gettext('Total Calling Time'), 'sortable': False, 'invisible': False},
        {'value': 'avg_call_time', 'text': gettext('Average Calling Time'), 'sortable': False, 'invisible': False}
    ]


def get_headers_campaign():
    return [
        {'value': 'name', 'text': gettext('Name'), 'sortable': True, 'invisible': False},
        {'value': 'call_campaign_id', 'text': gettext('Call Campaign'), 'sortable': True, 'invisible': False},
        {'value': 'created_time', 'text': gettext('Created Time'), 'sortable': True, 'invisible': False},
        {'value': 'owner', 'text': gettext('Owner'), 'sortable': False, 'invisible': False}
    ]


class CampaignPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        try:
            ordering = self.request.query_params.get('ordering', 'name')
        except KeyError as e:
            ordering = None
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'count': self.page.paginator.count,
            'ordering': ordering,
            'data': data,
            'header': get_headers_campaign()
        })


class CustomerPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        try:
            ordering = self.request.query_params.get('ordering', 'name')
        except KeyError as e:
            ordering = None
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'count': self.page.paginator.count,
            'ordering': ordering,
            'data': data['data'],
            'header': data['header']
        })


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        try:
            ordering = self.request.query_params.get('ordering', 'title')
        except KeyError as e:
            ordering = None
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'count': self.page.paginator.count,
            'ordering': ordering,
            'data': data
        })


def list_voice():
    return [
        {
            'voice': 'banmai',
            'title': 'Ban Mai'
        },
        {
            'voice': 'leminh',
            'title': 'Lê Minh'
        },
        {
            'voice': 'lannhi',
            'title': 'Lan Nhi'
        }
    ]


def convertTimestampToDatetime(timestamp):
    return datetime.fromtimestamp(timestamp / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S%z')


def convert_second_to_hour_minute_second(seconds):
    try:
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = (seconds % 3600) % 60
        return "{}:{:02d}:{:02d}".format(h, m, s)
    except Exception as e:
        print(e)
        return "00:00:00"


def convert_second_to_minute_second(seconds):
    try:
        seconds = int(seconds)
        m = (seconds % 3600) // 60
        s = (seconds % 3600) % 60
        if m == 0:
            return "{}s".format(s)
        else:
            if s == 0:
                return "{}m".format(m)
            else:
                return "{}m{}s".format(m, s)

    except Exception as e:
        print(e)
        return "00m00s"


def get_color_from_end_cause(end_cause):
    if end_cause == 'MANAGER_REQUEST':
        return gettext('#42be80')
    elif end_cause == 'NORMAL_CLEARING':
        return gettext('0F550C')
    elif end_cause == 'REDIRECTION_TO_NEW_DESTINATION':
        return gettext('#CA7D7D')
    elif end_cause == 'USER_BUSY':
        return gettext('#93A51B')
    elif end_cause == 'RECOVERY_ON_TIMER_EXPIRE':
        return gettext('#BAB6B6')
    elif end_cause == 'CALL_REJECTED':
        return gettext('#BAB6B6')
    return gettext('#BAB6B6')


def mask_phone_number(phone_number):
    return f"{phone_number[:-4]}xxxx"


def mask_customer_name(customer_name):
    length = len(customer_name)
    if length < 2:
        return customer_name
    length = int(length / 2)
    return f"{customer_name[:-length]}{'x':x^{length}}"


def html_escape_prompt(prompt: str):
    prompt = prompt.replace("<", "&lt;")
    prompt = prompt.replace(">", "&gt;")
    return prompt
