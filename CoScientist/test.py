from CoScientist.paper_parser.s3_connection import s3_service

if __name__=='__main__':
    s3_client = s3_service.create_s3_client()
    buckets = s3_client.list_buckets()
    print(buckets)