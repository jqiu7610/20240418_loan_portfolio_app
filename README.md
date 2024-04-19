# 20240418_loan_portfolio_app
https://djuew4gr4n.us-west-2.awsapprunner.com/

This project utilizes the German Credit Data from Kaggle to construct a loan portfolio. Analysis for the portfolio's characteristics are performed and responsive visual outputs are displayed below. Built using Python, Javascript, CSS, Flask, and hosted using AWS.
The plotly renders will take some time to load in, so pardon the inconvenience.

This app is capable of auto redeployment when data gets refreshed in the backend, if connected to SQL server through OBDC. For now, we will rely on the static German Credit Data gzip from Kaggle.


You can view the analysis notebook [here](https://github.com/jqiu7610/20240418_loan_portfolio_app/blob/main/01_analysis/notebook.ipynb)

You can view the html [here](https://github.com/jqiu7610/20240418_loan_portfolio_app/blob/main/02_local_app/templates/index.html)

You can view the flask app [here](https://github.com/jqiu7610/20240418_loan_portfolio_app/blob/main/02_local_app/app.py)