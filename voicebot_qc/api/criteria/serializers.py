from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from voicebot_qc.models import Criteria, DataInput


class CriteriaSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    type = serializers.CharField(required=True)
    data_input = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Criteria
        fields = ['id', 'name', 'description', 'is_required', 'is_monitor', 'type', 'config', 'data_input']
        read_only_fields = ['id']

    def get_data_input(self, obj):
        data_input = obj.data_input.all().values('source', 'field')
        return data_input

    @transaction.atomic()
    def create(self, validated_data):
        name = validated_data.get('name')
        campaign = validated_data.get('campaign')
        if Criteria.objects.filter(campaign=campaign, name=name).exists():
            raise ValidationError(detail='duplicate name, campaign')
        data_input_list = []
        data_input = validated_data.pop('data_input')
        for i in data_input:
            if DataInput.objects.filter(campaign=campaign, id=i).exists():
                data_input_list.append(DataInput(campaign=campaign, id=i))
            else:
                raise ValidationError(detail='data input invalid')
        instance = Criteria(**validated_data)
        instance.save()
        instance.data_input.set(data_input_list)
        return instance
