import json
import random
from datetime import datetime
from gettext import gettext
from html import escape

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, NotFound

from voicebot_qc.api.user_campaign.serializers import IdToEmailField
from voicebot_qc.elasticsearch.client import exec_query
from voicebot_qc.elasticsearch.query import get_calls_qc
from voicebot_qc.models import CallList, Call, DataInput


class JSONField(serializers.Field):
    default_error_messages = {
        'invalid': gettext('Value must be valid JSON.')
    }

    def to_representation(self, obj):
        try:
            data = json.loads(obj)
        except Exception:
            data = None
        return data

    def to_internal_value(self, data):
        try:
            data = json.dumps(data)
            data = escape(data, quote=False)
        except Exception:
            self.fail('invalid')
        return data


class CallListSerializer(serializers.ModelSerializer):
    assign_to = IdToEmailField(required=False, allow_null=True)
    created_by = IdToEmailField(required=False, allow_null=True)
    name = serializers.CharField(required=True)
    condition_config = JSONField(required=False, allow_null=True)

    class Meta:
        model = CallList
        fields = ['id', 'name', 'assign_to', 'created_by', 'status', 'condition_config', 'created_time']
        read_only_fields = ['id']

    @transaction.atomic()
    def create(self, validated_data):
        try:
            campaign = validated_data.get('campaign')
            # loads condition_config to get calls in call_list
            condition_config = json.loads(validated_data.get('condition_config', ''))
            amount = int(condition_config.get('amount', 100))
            from_time = condition_config.get('from_time', 0)
            to_time = condition_config.get('to_time', None)
            to_time = to_time if to_time else round(datetime.now().timestamp() * 1000)

            condition_list = condition_config.get('condition', [])

            es_query = get_calls_qc(campaign=campaign, amount=amount, from_time=from_time, to_time=to_time,
                                    condition_list=condition_list)
            res_es = exec_query(es_query)['responses'][0]['hits']['hits']

            # check if data or not
            if len(res_es) == 0:
                raise NotFound(detail='There are no calls that satisfy the condition')
            if len(res_es) < amount:
                raise NotFound(detail='There are only {} calls that satisfy the condition'.format(len(res_es)))

            calls = []
            call_list = CallList.objects.create(**validated_data)

            # get list data input of this campaign
            data_input_list = campaign.data_input.all().values_list('source', 'field')
            for i in res_es:
                call_data = i.get('_source')
                meta_data = {DataInput.SYSTEM: {}, DataInput.CUSTOMER_PROPERTIES: {}, DataInput.DATA_COLLECTION: {}}
                for data_input in data_input_list:
                    if data_input[0] == DataInput.SYSTEM:
                        meta_data[DataInput.SYSTEM][data_input[1]] = call_data.get(data_input[1])
                    if data_input[0] == DataInput.CUSTOMER_PROPERTIES:
                        meta_data[DataInput.CUSTOMER_PROPERTIES][data_input[1]] = call_data.get('customer').get(data_input[1])
                    if data_input[0] == DataInput.DATA_COLLECTION:
                        meta_data[DataInput.DATA_COLLECTION][data_input[1]] = call_data.get('data_collection').get(
                            data_input[1])
                ending_by = call_data.get('end_cause') if call_data.get('end_cause') else ''
                action_code = call_data.get('action_code') if call_data.get('action_code') else ''
                record_path = call_data.get('record_path') if call_data.get('record_path') else ''
                call = Call(call_list=call_list, call_id=call_data.get('id'), meta_data=json.dumps(meta_data),
                            start_time=call_data.get('start_time'), action_code=action_code,
                            ending_by=ending_by, record_path=record_path)
                calls.append(call)

            Call.objects.bulk_create(objs=calls, batch_size=1000)
            return call_list
        except Exception as e:
            raise ValidationError(detail=str(e))
