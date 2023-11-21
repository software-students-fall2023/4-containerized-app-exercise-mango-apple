# Containerized App Exercise

## Set up and run web app

Run the following commands to set up the web app in virtual environment:

First install pipenv
`pip install pipenv`

Initialize the virtual environment 
`pipenv shell`
`pipenv install`

Run the ml-client first:
`cd machine-learning-client`
Then:
`python ml_client.py`

Next, in another terminal, to run the app:
`cd web-app && flask --app app run`



Build a containerized app that uses machine learning. See [instructions](./instructions.md) for details.
