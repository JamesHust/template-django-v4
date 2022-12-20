from rest_framework import serializers

from voicebot_qc.models import Call


class CallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = ['id', 'call_id', 'start_time', 'action_code', 'ending_by', 'record_path', 'meta_data', 'status']
        read_only_fields = ['id', 'call_id', 'start_time', 'action_code', 'ending_by', 'record_path', 'meta_data']
