import uuid
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Campaign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    call_campaign_id = models.CharField(max_length=50, default="", blank=False)
    name = models.CharField(max_length=128, blank=False)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='campaigns', on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'campaign_qc'

    def __str__(self):
        return self.name

    def delete(self):
        self.is_deleted = True
        self.save()


class CallList(models.Model):
    """
    list of call need QC
    """
    OPEN = 'open'
    CLOSE = 'close'
    STATUS_CHOICE = (
        (OPEN, 'Open'),
        (CLOSE, 'Close')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, default="", null=False)
    campaign = models.ForeignKey(Campaign, related_name='call_lists', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name='created_call_lists', on_delete=models.CASCADE)
    assign_to = models.ForeignKey(User, related_name='assigned_call_lists', on_delete=models.CASCADE, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICE, default=OPEN)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    condition_config = models.TextField(blank=True, help_text="list json string format")

    class Meta:
        db_table = 'call_list_qc'
        unique_together = ['name', 'campaign']

    def __str__(self):
        return self.name


class Criteria(models.Model):
    """
    criteria need define when create campaign
    """
    BOOL = 'BOOL'
    ENUM = 'ENUM'
    TEXT = 'TEXT'
    TYPE_CHOICES = [
        (BOOL, 'Boolean'),
        (ENUM, 'Enumerate'),
        (TEXT, 'Text')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, related_name='criterias', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="", null=False)
    description = models.TextField(blank=True)
    is_required = models.BooleanField(default=True)
    is_monitor = models.BooleanField(default=True)
    type = models.CharField(max_length=25, blank=False, choices=TYPE_CHOICES)
    config = models.TextField(blank=True, help_text="separated by ;")
    data_input = models.ManyToManyField('DataInput', blank=True, related_name='data_input_criterias')
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'criteria_qc'
        unique_together = ('name', 'campaign')

    def __str__(self):
        return self.name


class Call(models.Model):
    """
    call need QC
    """
    NOT_WORKING = 'not_working'
    WORKING = 'working'
    DONE = 'done'
    STATUS_CHOICE = (
        (NOT_WORKING, 'Not working'),
        (WORKING, 'Working'),
        (DONE, 'Done')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    call_list = models.ForeignKey(CallList, related_name='calls', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    call_id = models.CharField(max_length=50, default="", blank=False)
    meta_data = models.TextField(help_text='string json format {}', default="", blank=True)
    start_time = models.DateTimeField(null=True)
    action_code = models.CharField(max_length=256, default="", blank=True)
    ending_by = models.CharField(max_length=256, default="", blank=True)
    record_path = models.CharField(max_length=256, default="", blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICE, default=NOT_WORKING)
    comment = models.TextField(default="", blank=True)

    class Meta:
        db_table = 'call_qc'
        unique_together = ('call_list', 'call_id')

    def __str__(self):
        return self.call_id


class Record(models.Model):
    """
    1 call + 1 criteria --> 1 record || data_output
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    call = models.ForeignKey(Call, related_name='records', on_delete=models.CASCADE)
    criteria = models.ForeignKey(Criteria, related_name='records', on_delete=models.CASCADE)
    result = models.TextField(blank=True)
    comment = models.TextField(blank=True)

    class Meta:
        db_table = 'record'
        unique_together = ('call', 'criteria')

    def __str__(self):
        return f"{self.criteria.name}.{self.call.call_id}"


class DataInput(models.Model):
    CUSTOMER_PROPERTIES = "customer_properties"
    DATA_COLLECTION = "data_collection"
    SYSTEM = "system"
    SOURCE_CHOICES = (
        (CUSTOMER_PROPERTIES, 'Customer properties'),
        (DATA_COLLECTION, 'Data collection'),
        (SYSTEM, "System")
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.CharField(max_length=50, blank=False, choices=SOURCE_CHOICES)
    field = models.CharField(max_length=255, blank=False)
    campaign = models.ForeignKey(Campaign, related_name='data_input', on_delete=models.CASCADE, default='')

    class Meta:
        db_table = 'data_input'
        unique_together = ('source', 'field', 'campaign')

    def __str__(self):
        return f"{self.campaign.id}.{self.source}.{self.field}"


class UserCampaign(models.Model):
    QC_MEMBER = "qc_member"
    QC_LEAD = "qc_lead"
    PERMISSION_CHOICE = (
        (QC_MEMBER, 'QC member'),
        (QC_LEAD, 'QC lead'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey('Campaign', related_name='user_campaigns', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user_user_campaigns', on_delete=models.CASCADE)
    permission = models.CharField(max_length=15, blank=False, choices=PERMISSION_CHOICE)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='created_user_campaigns', on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_campaign'
        unique_together = ['campaign', 'user']
