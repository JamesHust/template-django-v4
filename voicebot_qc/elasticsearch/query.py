from voicebot_qc.models import DataInput


def query_get_call_from_to(campaign_id, from_time, to_time):
    return {
        "bool": {
            "must": [
                {
                    "match_phrase": {
                        "campaign.id": {
                            "query": campaign_id
                        }
                    }
                },
                {
                    "range": {
                        "start_time": {
                            "gte": from_time,
                            "lte": to_time,
                            "format": "epoch_millis"
                        }
                    }
                }
            ]
        }
    }


# get random call to QC
def map_operator_filter(condition, field):
    filter = {}
    # operator is '='
    if condition['operator'] == '=':
        filter = {"term": {field: condition['value']}}
    # operator is '>'
    if condition['operator'] == '&gt;':
        filter = {"range": {
            field: {
                "gt": condition['value'],
            }
        }}
    # operator is '<'
    if condition['operator'] == '&lt;':
        filter = {"range": {
            field: {
                "lt": condition['value'],
            }
        }}
    return filter


def get_calls_qc(campaign, amount: int, from_time, to_time, condition_list):
    sub_query = query_get_call_from_to(campaign.call_campaign_id, from_time, to_time)
    for condition in condition_list:
        if condition['source'] == DataInput.CUSTOMER_PROPERTIES:
            field = '{}.{}'.format('customer', condition['field'])
        elif condition['source'] == DataInput.DATA_COLLECTION:
            field = '{}.{}'.format('data_collection', condition['field'])
        else:
            field = condition['field']
        filter = map_operator_filter(condition, field)
        if filter != {}:
            sub_query['bool']['must'].append(filter)

    query = {
        "query": sub_query,
        "sort": {
            "_script": {
                "script": "Math.random()",
                "type": "number",
                "order": "asc"
            }
        },
        "size": amount,
    }
    return query
