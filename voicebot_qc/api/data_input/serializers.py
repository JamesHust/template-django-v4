from rest_framework import serializers

from voicebot_qc.models import DataInput


class DataInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataInput
        fields = ['id', 'source', 'field']
        read_only_fields = ['id']
