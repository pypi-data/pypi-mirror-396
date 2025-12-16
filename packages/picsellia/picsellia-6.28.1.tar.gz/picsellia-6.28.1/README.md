# Picsellia SDK

Picsellia Python SDK is a python library that allows connecting to Picsellia platform.

## Documentation

Reference of the SDK can be found at [reference](https://documentation.picsellia.com/reference/client)

## Getting started
Documentation can be found at [docs](https://documentation.picsellia.com/docs/getting-started).
Start by installing the Picsellia python package in your environment.
```
pip install picsellia
```

Then, initialize a client
```python
from picsellia import Client
client = Client(api_token="<your api token>")
```

Now, use it to upload data and create a dataset !
```python
lake = client.get_datalake()
uploaded_data = lake.upload_data(filepaths=["pics/twingo.png", "pics/ferrari.png"], tags=["tag_car"])

dataset = client.create_dataset("cars").create_version("first")
dataset.add_data(uploaded_data)
```

## What is Picsellia ?

Our mission is to give you all the necessary tools to relieve the burden of AI projects off of your shoulders. As a data scientist / ML engineer / Researcher, you shouldn't have to worry about the following topics :

- [💾 Data Management](https://documentation.picsellia.com/docs/data-management)
- [📈 Experiment Tracking](https://documentation.picsellia.com/docs/experiment-tracking)
- [📘 Model Management](https://documentation.picsellia.com/docs/export-an-experiment)
- [🚀 Model Deployment](https://documentation.picsellia.com/docs/serverless)
- [👀 Model Monitoring](https://documentation.picsellia.com/docs/monitor-model)

Picsellia is the one-stop place for all the life-cycle of your Computer Vision projects, from ideation to production in a single platform 🚀.
