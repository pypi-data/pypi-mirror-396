# bpx-dataio

Useful utilities for data IO operations, including Snowflake, S3, and SageMaker integrations.

## Installation

```bash
pip install bpx-dataio
```

## Classes

### SnowflakeIO

Handles authentication and interaction with a Snowflake data warehouse using AWS Secrets Manager credentials.

```python
from dataio import SnowflakeIO

# Initialize with default settings
sf = SnowflakeIO()

# Execute a query
df = sf.query("SELECT * FROM my_table LIMIT 10")

# Execute a command
sf.execute_command("CREATE TABLE IF NOT EXISTS my_table (id INT)")
```

### PARAM_JSON_IO

Read and write parameters to JSON files.

```python
from dataio import PARAM_JSON_IO

# Initialize with JSON file path
json_io = PARAM_JSON_IO("config.json")

# Read parameters
params = json_io.read_param_from_json()

# Write/update parameters
json_io.write_param_to_json({"key": "value"})
```

### SAGEMAKER_INFO

Get SageMaker session and AWS information. Only works in SageMaker environments.

```python
from dataio import SAGEMAKER_INFO

sm_info = SAGEMAKER_INFO(region='us-west-2', verbose=True)
session = sm_info.get_sagemaker_session()
role_arn = sm_info.get_execution_role()
```

### DATAIO_S3

S3 operations for uploading and downloading data.

```python
from dataio import DATAIO_S3

s3_io = DATAIO_S3()

# List objects in a bucket
objs = s3_io.list_bucket_objs("my-bucket", prefix="data/")

# Upload a file
s3_io.upload_file_to_bucket("local_file.csv", "my-bucket", "remote_file.csv")

# Upload a DataFrame
import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3]})
s3_io.upload_dataframe_to_bucket(df, "my-bucket", "data.csv")

# Read a DataFrame from S3
df = s3_io.read_df_from_bucket("my-bucket", "data.csv")
```

### SCALER

Custom scaler that applies scaling to each column independently, compatible with scikit-learn pipelines.

```python
from dataio import SCALER
from sklearn.preprocessing import RobustScaler
import pandas as pd

scaler = SCALER(scaler=RobustScaler)
df = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [10, 20, 30, 40, 50]})

# Fit and transform
df_scaled = scaler.fit_transform(df)

# Transform only
df_scaled = scaler.transform(df)

# Inverse transform
df_original = scaler.inverse_transform(df_scaled)
```

## Requirements

- Python >= 3.7
- boto3 >= 1.26.0
- snowflake-connector-python[pandas] >= 3.0.0
- pandas >= 1.5.0
- numpy >= 1.23.0
- sagemaker >= 2.0.0
- scikit-learn >= 1.0.0

## License

MIT License

## Author

Julian Liu

