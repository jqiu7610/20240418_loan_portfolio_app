# app
from flask import Flask, render_template, request, Response
from functions_app import *
import json
import pandas as pd
import boto3
import numpy as np
from io import StringIO
import plotly
import plotly.express as px

try:
	from passwords import *
	bool_debug = True
except:
	bool_debug = False
	AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
	AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# instantiate app
application = Flask(__name__)

# make a global variable
dict_contents = {}

# constants
str_project = '20240418-loan-portfolio-app'

@application.route('/download/<str_file_key>')
def download(str_file_key):
	# get data frame from dictionary
    df = dict_contents[str_file_key]
    # convert to csv
    csv_output = StringIO()
    df.to_csv(csv_output, index=False)
    # move cursor to the beginning
    csv_output.seek(0)
    # get dates
    date_file = dict_contents['date_file']
    str_filename = f"{date_file}_{str_file_key}.csv"
    # return response
    return Response(
        csv_output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={str_filename}"}
    )

# show page for entering big account id
@application.route('/')
def show_home_page():
	# make global
	global dict_contents

	# create session
	cls_session = boto3.Session(
		aws_access_key_id=AWS_ACCESS_KEY_ID,
		aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
	)
	# initialize client
	cls_client = cls_session.client('s3')

	# get date info
	today = pd.Timestamp.now()
	date_file = today.strftime('%Y%m%d')
	date_format = today.strftime('%Y-%m-%d')

	# assign
	dict_contents['today'] = today
	dict_contents['date_file'] = date_file
	dict_contents['date_format'] = date_format

	# #################################################################################
	# # df_credit_risk_active
	# #################################################################################
	# read df all
	# originations today
	str_filename = 'df_credit_risk_active.gzip'
	str_key = f'01_analysis/output/{str_filename}'
	df = read_parquet_from_s3(
		cls_client=cls_client, 
		str_project=str_project,
		str_key=str_key,
	)

	# assign
	print('Assigning to dict_contents...')
	dict_contents['df_credit_risk_active'] = df


	# create plot of tier comp ACTIVE accounts
	#----------------------------------------------------------------------------------
	print('Making PlotlyJSONEncoder 1')
	# Count the frequency of each category
	category_counts = df['loan_grade'].value_counts().reset_index()
	category_counts.columns = ['loan_grade', 'count']
	# Create a pie chart using Plotly Express
	fig = px.pie(category_counts, values='count', names='loan_grade')
	str_title = 'Distribution of Loan Tiers Active Accounts'
	# update title
	fig.update_layout(title={'text': str_title, 'x': 0.5, 'xanchor': 'center'})
	# Adjust figure size
	fig.update_layout(width=800, height=600)
	# make json
	graphJSON_loan_tiers_active = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


	# create plot of loan intent distribution ACTIVE accounts
	#----------------------------------------------------------------------------------
	# Count the frequency of each category
	print('Making PlotlyJSONEncoder 2')	
	category_counts = df['loan_intent'].value_counts().reset_index()
	category_counts.columns = ['loan_intent', 'count']
	# Create a pie chart using Plotly Express
	fig = px.pie(category_counts, values='count', names='loan_intent')
	str_title = 'Distribution of Loan Intent Active Accounts'
	# update title
	fig.update_layout(title={'text': str_title, 'x': 0.5, 'xanchor': 'center'})
	# Adjust figure size
	fig.update_layout(width=800, height=600)
	# make json
	graphJSON_loan_intent_active = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


	# create plot of apr vs default history ACTIVE accounts 
	#----------------------------------------------------------------------------------
	print('Making PlotlyJSONEncoder 3')
	# get avg apr for default history
	avg_apr_default_history = df.groupby('cb_person_default_on_file')['loan_int_rate'].mean().reset_index()
	avg_apr_default_history.replace({'N':'No Default History', 'Y':'Has Default History'}, inplace=True)
	# plotly avg apr vs default history
	fig = px.bar(avg_apr_default_history, x='cb_person_default_on_file', y='loan_int_rate',
		labels={'cb_person_default_on_file': 'Default History', 'loan_int_rate': 'Average Interest Rate (%)'})
	str_title = 'Average APR for Default History Active Accounts'
	# update title
	fig.update_layout(title={'text': str_title, 'x': 0.5, 'xanchor': 'center'})
	# Adj fig size
	fig.update_layout(width=800, height=600)	
	graphJSON_apr_vs_default_history_active = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


	# create plot of apr vs tiers ACTIVE accounts 
	#----------------------------------------------------------------------------------
	print('Making PlotlyJSONEncoder 4')
	# get avg apr for loan grades
	avg_apr_tiers = df.groupby('loan_grade')['loan_int_rate'].mean().reset_index()
	# plotly avg apr vs default history
	fig = px.bar(avg_apr_tiers, x='loan_grade', y='loan_int_rate',
		labels={'loan_grade': 'Tiers', 'loan_int_rate': 'Average Interest Rate (%)'})
	str_title = 'Average APR for Loan Tiering Active Accounts'
	# update title
	fig.update_layout(title={'text': str_title, 'x': 0.5, 'xanchor': 'center'})
	# Adj fig size
	fig.update_layout(width=800, height=600)
	graphJSON_apr_vs_tiers_active = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


	# create plot of apr vs tiers ACTIVE accounts 
	#----------------------------------------------------------------------------------
	print('Making PlotlyJSONEncoder 5')
	# get avg apr for loan grades
	avg_apr_income = df.groupby('loan_grade')['loan_percent_income'].mean().reset_index()
	# plotly avg apr vs default history
	fig = px.bar(avg_apr_income, x='loan_grade', y='loan_percent_income', 
		labels={'loan_grade': 'Tiers', 'loan_percent_income': 'Average Income Utilization for Loan Amount (%)'})
	str_title = 'Average APR for Income Utilization for Loan on Active Accounts'
	# update title
	fig.update_layout(title={'text': str_title, 'x': 0.5, 'xanchor': 'center'})
	# Adj fig size
	fig.update_layout(width=800, height=600)
	graphJSON_income_util_active = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	

	# make sortable table
	#----------------------------------------------------------------------------------
	print('Making sortable table...')
	df_credit_risk_active = create_sortable_table(df=df)


	# #################################################################################
	# # df_credit_risk
	# #################################################################################
	# read df
	# originations today
	str_filename = 'df_credit_risk.gzip'
	str_key = f'01_analysis/output/{str_filename}'
	df = read_parquet_from_s3(
		cls_client=cls_client, 
		str_project=str_project,
		str_key=str_key,
	)

	# assign
	print('Assigning to dict_contents...')
	dict_contents['df_credit_risk'] = df

	# create plot loan status
	#----------------------------------------------------------------------------------
	print('Making PlotlyJSONEncoder 6')
	# Count the frequency of each category
	status_counts = df['loan_status'].value_counts().reset_index()
	status_counts.replace({0:'Terminated', 1:'Active'}, inplace=True)
	status_counts.columns = ['loan_status', 'count']
	# Create a pie chart using Plotly Express
	fig = px.pie(status_counts, values='count', names='loan_status')
	str_title = 'Loan Status'
	# update title
	fig.update_layout(title={'text': str_title, 'x': 0.5, 'xanchor': 'center'})
	# Adjust figure size
	fig.update_layout(width=800, height=600)
	# make json
	graphJSON_loan_status = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


	# create plot loan volume
	#----------------------------------------------------------------------------------
	# get avg apr for loan grades
	print('Making PlotlyJSONEncoder 7')
	volume_ = df.groupby('loan_status')['loan_amnt'].sum().reset_index()
	volume_.replace({0:'Terminated', 1:'Active'}, inplace=True)
	volume_.columns = ['loan_status', 'volume']
	# Create a pie chart using Plotly Express
	fig = px.pie(volume_, values='volume', names='loan_status')
	str_title = 'Loan Portfolio Volume Active/Terminated (%/$)'
	# update title
	fig.update_layout(title={'text': str_title, 'x': 0.5, 'xanchor': 'center'})
	# Adjust figure size
	fig.update_layout(width=800, height=600)
	# make json
	graphJSON_loan_volume = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


	# create plot apr vs loan tier
	#----------------------------------------------------------------------------------
	print('Making PlotlyJSONEncoder 8')
	# get avg apr for loan grades
	avg_apr_tiers = df.groupby('loan_grade')['loan_int_rate'].mean().reset_index()
	# plotly avg apr vs loan tier
	fig = px.bar(avg_apr_tiers, x='loan_grade', y='loan_int_rate', 
		labels={'loan_grade': 'Tiers', 'loan_int_rate': 'Average Interest Rate (%)'})
	str_title = 'Average APR for Loan Tiers LTD'
	# update title
	fig.update_layout(title={'text': str_title, 'x': 0.5, 'xanchor': 'center'})
	# Adj fig size
	fig.update_layout(width=800, height=600)	
	# make json
	graphJSON_loan_tiers = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

	# create plot apr vs income utilization
	#----------------------------------------------------------------------------------
	print('Making PlotlyJSONEncoder 9')
	# get avg apr for loan grades
	avg_apr_income = df.groupby('loan_grade')['loan_percent_income'].mean().reset_index()
	avg_apr_income.replace({'N':'No Default History', 'Y':'Has Default History'}, inplace=True)
	# plotly avg apr vs default history
	fig = px.bar(avg_apr_income, x='loan_grade', y='loan_percent_income', 
		labels={'loan_grade': 'Tiers', 'loan_percent_income': 'Average Income Utilization for Loan Amount (%)'})
	str_title = 'Average APR vs Income Utilization for Loan LTD'
	# update title
	fig.update_layout(title={'text': str_title, 'x': 0.5, 'xanchor': 'center'})
	# Adj fig size
	fig.update_layout(width=800, height=600)
	# make json
	graphJSON_income_util = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

	# make sortable table
	#----------------------------------------------------------------------------------
	print('Making sortable table...')
	df_credit_risk = create_sortable_table(df=df)

	#################################################################################
	# SHOW HOME PAGE
	#################################################################################
	return render_template(
		'index.html',
		today=today,
		date_format=date_format,		
		df_credit_risk_active=df_credit_risk_active,
		df_credit_risk=df_credit_risk,
		graphJSON_loan_status=graphJSON_loan_status,
		graphJSON_loan_intent_active=graphJSON_loan_intent_active,
		graphJSON_apr_vs_default_history_active=graphJSON_apr_vs_default_history_active,
		graphJSON_apr_vs_tiers_active=graphJSON_apr_vs_tiers_active,
		graphJSON_income_util_active=graphJSON_income_util_active,
		graphJSON_loan_volume=graphJSON_loan_volume,
		graphJSON_loan_tiers=graphJSON_loan_tiers,
		graphJSON_income_util=graphJSON_income_util,

	)

# run app		
if __name__ == '__main__':
	application.run(host="0.0.0.0", debug=False) # True for local testing