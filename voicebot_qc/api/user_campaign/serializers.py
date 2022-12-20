from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from openpyxl import load_workbook

from voicebot_qc.models import UserCampaign, CallList


class IdToEmailField(serializers.Field):
    def to_representation(self, obj):
        return obj.email

    def to_internal_value(self, data):
        try:
            user = User.objects.get(email=data)
            return user
        except ObjectDoesNotExist:
            raise NotFound(detail="User Not Found")


class UserCampaignSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email', max_length=255)

    class Meta:
        model = UserCampaign
        fields = ['email', 'permission', 'id']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        permission = validated_data.pop('permission')
        instance.permission = permission
        instance.save()
        return instance


def file_validation(file):
    try:
        wb = load_workbook(file, read_only=True)
    except Exception as e:
        raise ValidationError(detail=gettext('Cannot upload this excel file. Please enable editing mode.'))
    try:
        ws = wb.worksheets[0]
    except Exception as e:
        raise ValidationError(detail=gettext('File has no sheet"'))
    return ws


class ImportPermissionsSerializer(serializers.Serializer):
    file = serializers.FileField(allow_null=False, write_only=True, validators=[file_validation])

    class Meta:
        fields = ['file']
