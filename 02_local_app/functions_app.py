import pandas as pd
from io import StringIO

# get object from s3
def get_object_from_s3(cls_client, str_bucket, str_key):
	s3_object = cls_client.get_object(Bucket=str_bucket, Key=str_key)
	bytes_object = s3_object['Body'].read().decode('utf-8')
	df = pd.read_csv(StringIO(bytes_object))
	return df

# static table
def create_static_table(df):
	df = df.to_html(index=False, header='true', justify='left')
	return df

# sortable table
def create_sortable_table(df):
	df = df.to_html(classes='display', escape=False, index=False)
	return df