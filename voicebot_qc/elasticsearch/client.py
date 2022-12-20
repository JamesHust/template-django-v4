import os

from voicebot_qc.elasticsearch import es


def exec_query(query, index=None):
    if not index:
        index = f"{os.getenv('ES_LOG_INDEX', 'callcenter')}-*"
    i = {"index": index, "ignore_unavailable": True,
         "preference": 1571281333186}
    return es.msearch(body=[i, query])


