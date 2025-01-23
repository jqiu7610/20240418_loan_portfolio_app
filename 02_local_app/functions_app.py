import pandas as pd
import io
from io import StringIO
from io import BytesIO

# get object from s3
def get_object_from_s3(cls_client, str_bucket, str_key):
	s3_object = cls_client.get_object(Bucket=str_bucket, Key=str_key)
	bytes_object = s3_object['Body'].read().decode('utf-8')
	df = pd.read_csv(StringIO(bytes_object))
	return df

# read parquet from s3
def read_parquet_from_s3(cls_client, str_project, str_key):
	obj_parquet = cls_client.get_object(Bucket=str_project, Key=str_key)
	parquet_content = io.BytesIO(obj_parquet['Body'].read())
	df = pd.read_parquet(parquet_content)
	return df
# static table
def create_static_table(df):
	df = df.to_html(index=False, header='true', justify='left')
	return df

# sortable table
def create_sortable_table(df):
	df = df.to_html(classes='display', escape=False, index=False)
	return df

# download from s3
def download_from_s3(cls_client, str_local_path, str_bucket_path, str_project):
	# download file
	cls_client.download_file(
		str_project, 
		str_bucket_path, 
		str_local_path,
	)
