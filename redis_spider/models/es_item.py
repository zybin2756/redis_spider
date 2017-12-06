from elasticsearch_dsl import DocType, Date, Integer, Keyword, Text, Completion
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

# Define a default Elasticsearch client
connections.create_connection(hosts=['localhost'])


#解决elasticsearch_dsl suggest的bug
# class CustonAnalyzer(_CustomAnalyzer):
#     def get_analysis_definition(self):
#         return {}
#
# ik_work = CustonAnalyzer("ik_max_word",filter=["lowercase"])


class es_JobType(DocType):
    suggest = Completion(analyzer="ik_max_word")
    job_name = Text(analyzer="ik_max_word")
    min_salary = Integer()
    max_salary = Integer()
    url = Text()
    city = Keyword()
    company_name = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")
    publish_time = Date()
    crawl_time = Date()
    exp = Keyword()
    degree = Keyword()
    company_type = Text(analyzer="ik_max_word")

    class Meta:
        index = "lagou"
        doc_type = "job"

if __name__ == "__main__":
    es_JobType.init()
