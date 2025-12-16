import sys
import time
import json
import boto3
import certifi
import logging
import argparse
import sagemaker
import numpy as np
import pandas as pd 
from io import StringIO
import snowflake.connector 
from typing import Optional
from datetime import datetime
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler


# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class SnowflakeIO:
    """
    Handles authentication and interaction with a Snowflake data warehouse using
    AWS Secrets Manager credentials.
    """

    def __init__(self, args: Optional[argparse.Namespace] = None):
        """
        Initializes a Snowflake connection using credentials stored in AWS Secrets Manager.

        Parameters:
        - args (argparse.Namespace): Optional. Parsed arguments with Snowflake connection config.
        """
        if args is None:
            logger.info("No 'args' provided. Setting default snowflake parameters, which can be updated later.")
            parser = argparse.ArgumentParser(description="Snowflake connection configuration.")
            parser.add_argument("--region_name", type=str, default="us-west-2", help="AWS region for Secrets Manager")
            parser.add_argument("--secrets_name", type=str, default="AmazonSageMaker-DataWranglerSnowflakeCreds", help="Name of AWS secret")
            parser.add_argument("--role", type=str, default="SAGEMAKER_DSCI_TEST", help="Snowflake role")
            parser.add_argument("--warehouse", type=str, default="READER_WH", help="Snowflake warehouse")
            parser.add_argument("--database", type=str, default="ENTERPRISEDATALAKE_PROD", help="Snowflake database")
            parser.add_argument("--schema", type=str, default="DEV", help="Snowflake schema")
            args, _ = parser.parse_known_args()

        self.args = args
        logger.info("Initializing SnowflakeIO with parameters: %s", vars(self.args))

        self.conn = self._connect()

    def _connect(self):
        """
        Internal method to establish a Snowflake connection using credentials from Secrets Manager.
        """
        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager', region_name=self.args.region_name)

        secret_value = client.get_secret_value(SecretId=self.args.secrets_name)
        creds = json.loads(secret_value['SecretString'])

        logger.info("Establishing connection to Snowflake...")
        conn = snowflake.connector.connect(
            user=creds['username'],
            password=creds['password'],
            account=creds['accountid'],
            warehouse=self.args.warehouse,
            database=self.args.database,
            schema=self.args.schema,
            role=self.args.role,
            protocol="https",
            port=443,
            session_parameters={'CLIENT_SESSION_KEEP_ALIVE': True},
            ssl_ca_cert=certifi.where()
        )
        logger.info("Snowflake connection established successfully.")
        return conn

    def query(self, sql_query: str) -> pd.DataFrame:
        """
        Execute a SQL query and return the result as a Pandas DataFrame.

        Parameters:
        - sql_query (str): The SQL query string to execute.

        Returns:
        - pd.DataFrame: Result of the query.
        """
        logger.info("Executing SQL query: %s", sql_query)
        with self.conn.cursor() as cursor:
            result = cursor.execute(sql_query).fetch_pandas_all()
        return result

    def execute_command(self, command: str) -> None:
        """
        Execute a SQL command that doesn't return data (e.g. CREATE, INSERT, etc.).

        Parameters:
        - command (str): The SQL command string to execute.
        """
        logger.info("Executing SQL command: %s", command)
        with self.conn.cursor() as cursor:
            cursor.execute(command)

class PARAM_JSON_IO:
    ''' function to read json file, add or update param to json file '''
    
    # import json
    
    def __init__(self, json_path=None):
        self.json_path = json_path

    def read_param_from_json(self):

        try:
            with open(self.json_path, 'r') as f_in:
                self.params = json.load(f_in)   
            print(f'loading {self.json_path}\n')  
            
            return self.params
        
        except Exception as err:
            print(err)
        
    
    def write_param_to_json(self, param=None):
    
        try:
            self.read_param_from_json()
        
        except Exception as err:
            self.params = {}
            print('creating a new dictionary to store params!')

        finally:
            self.params.update(param) # if param in params, update the param; if not, add the param
            with open(self.json_path, 'w') as f_out:
                f_out.write(json.dumps(self.params))
                print(f'\nWRITE TO: {self.json_path}!')  
                
            return self.params

        
class SAGEMAKER_INFO:
    def __init__(self, region='us-west-2', verbose=False):
        """
        run below commands to reimport module after making changes to the module
        import sys
        from importlib import reload
        reload(sys.modules['utils_sagemaker'])
        """
        
        #         import boto3
        #         import sagemaker
        #         from botocore.config import Config

        print('This only works in SageMaker environment!')
        self.verbose = verbose
        
        # boto3
        self.boto_session = boto3.Session(region_name=region)
        self.region = self.boto_session.region_name
        self.s3_resource = self.boto_session.resource('s3')
        
        if self.verbose:
            print("['boto_session']: {}".format(self.boto_session))
            print("['region']: {}".format(self.region))
            print("['s3_resource']: {}".format(self.s3_resource))

        # boto3 again
        self.s3_client = self.boto_session.client(service_name="s3", region_name=self.region)
        self.sagemaker_client = self.boto_session.client(service_name='sagemaker')
        self.sagemaker_runtime = boto3.client(service_name='sagemaker-runtime')
        
        if self.verbose:
            print(f"S3 Client ['s3_client']: {self.s3_client}")
            print(f"SageMaker Client ['sagemaker_client']: {self.sagemaker_client}")
        
        # account id
        self.account_id = boto3.client("sts").get_caller_identity().get("Account")
        if self.verbose: print("Account ID['account_id']: {}".format(self.account_id))
        
        # iam client
        # self.config = Config(retries={"max_attempts": 10, "mode": "adaptive"})
        self.iam_client = boto3.client("iam", region_name=self.region) # config=self.config, 
        if self.verbose: print('[iam_client]: ', self.iam_client)
            
    def get_sagemaker_session(self):
        # sagemaker
        self.sagemaker_session = sagemaker.session.Session(boto_session=self.boto_session)
        self.default_bucket = self.sagemaker_session.default_bucket()

        if self.verbose:
            print("['sagemaker_session']: {}".format(self.sagemaker_session))
            print("['default_bucket']: {}".format(self.default_bucket))
    
        return self.sagemaker_session
    
    def get_athena_client(self):
        
        self.athena_client = boto3.client('athena', region_name=self.region)
        if self.verbose: print(f"Athena lient ['athena_client']: {self.athena_client}")
        
    def get_featurestore_session(self):
        # feature store runtime
        self.featurestore_runtime = self.boto_session.client(service_name='sagemaker-featurestore-runtime',  region_name=self.region)      
        self.featurestore_session = sagemaker.Session(boto_session=self.boto_session, sagemaker_client=self.sagemaker_client, sagemaker_featurestore_runtime_client=self.featurestore_runtime)               
        
        if self.verbose:
            print(f"Feature Store Runtime ['featurestore_runtime']: {self.featurestore_runtime}")
            print(f"Feature Store Session ['featurestore_session']: {self.featurestore_session}")
        
        return self.featurestore_session
    
    def _resolve_sm_role(self):
        
        response_roles = self.iam_client.list_roles(PathPrefix='/', MaxItems=999) # Marker='string',
        
        try:
            for role in response_roles['Roles']:
                if role['RoleName'].startswith('AmazonSageMaker-ExecutionRole-'):
                    # print('Resolved SageMaker IAM Role to: ' + str(role))
                    self.role_arn = role['Arn']
                    self.role_name = role['RoleName']

                    if self.verbose:
                        print("['role_arn']: {}".format(self.role_arn))
                        print("['role_name']: {}".format(self.role_name))
        except:
            raise Exception('Could not resolve what should be the SageMaker role to be used')
                
    def get_execution_role(self):
        
        # get_execution_role only work in notebook instance, it will fail when running on other instance!
        try:
            self.role_arn = sagemaker.get_execution_role()
            self.role_name = self.role_arn.split("/")[-1]
            
            if self.verbose:
                print("['role_arn']: {}".format(self.role_arn))
                print("['role_name']: {}".format(self.role_name))
            
            return self.role_arn
        
        except ValueError:
            # print(ValueError)
            try:
                self._resolve_sm_role()
                return self.role_arn
            except:
                print('Error retrieving role_arn!')
 
class DATAIO_S3(SAGEMAKER_INFO):
    
    def __init__(self):
        super().__init__()

    def list_bucket_objs(self, bucket_name, prefix=None, obj_type=None):

        bucket = self.s3_resource.Bucket(bucket_name)

        if prefix is None:
            objs =  [obj.key for obj in bucket.objects.all()]
        else:
            objs = [obj.key for obj in bucket.objects.filter(Prefix=prefix)]

        if obj_type is not None:
            objs = [obj for obj in objs if obj_type in str(obj)]

        return objs

    def upload_file_to_bucket(self, file_name, bucket_name, obj_name):

        self.s3_resource.meta.client.upload_file(file_name, bucket_name, obj_name)
        print(f'Upload {file_name} to S3 bucket {bucket_name} as {obj_name}')
        
    def upload_dataframe_to_bucket(self, dataframe, bucket_name, obj_name, index=True):
        
        """ index parameter needs to be True. Training job automatically removes first column as it considers as index, not part of data"""
        
        # Convert DataFrame to CSV format in memory
        csv_buffer = StringIO()
        dataframe.to_csv(csv_buffer, index=index)
        
        self.s3_client.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=obj_name)
        print(f'Upload dataframe to S3 bucket {bucket_name} as {obj_name}')

    def upload_tar_to_bucket(self, tar_file:str, bucket_name, obj_name:str):
        
        # if not obj_name.endswith('tar.gz.'): obj_name = obj_name + '.tar.gz.'
        
        with open(tar_file,'rb') as tar:
            self.s3_client.upload_fileobj(tar, bucket_name, obj_name)
        print(f'Upload {tar_file} to S3 bucket {bucket_name} as {obj_name}')

    def read_df_from_bucket(self, bucket_name, key):

        response = self.s3_client.get_object(Bucket=bucket_name, Key=key)
        csv_string = response['Body'].read().decode('utf-8')
        self.df = pd.read_csv(StringIO(csv_string))
        self.df.drop(columns=[i for i in self.df if 'Unnamed' in i], inplace=True)

        return self.df
    
    def read_json_from_bucket(self, bucket_name, key):

        response = self.s3_client.get_object(Bucket=bucket_name, Key=key)
        json_string = response['Body'].read().decode('utf-8')
        self.params = json.load(StringIO(json_string))

        return self.params



class SCALER(BaseEstimator, TransformerMixin):
    def __init__(self, scaler=RobustScaler):
        print('Scaler use: ',scaler)
        self.scaler = scaler
    
    def fit(self, df):

        self.data = {k: np.array(list(v.values())) for (k, v) in df.to_dict().items()}
        self.scalers = {k: self.scaler() for (k, v) in df.to_dict().items()}
        
        for key, data in self.data.items():
            data = data.reshape((-1, 1))
            self.scalers[key].fit(data)
    
    def transform(self, df):
        results = list()
        for key, data in df.to_dict().items():
            data = np.array(list(data.values())).reshape((-1, 1))
            scaled_data = self.scalers[key].transform(data).flatten()
            results.append(scaled_data)

        df = pd.DataFrame(np.array(results).T, columns=df.columns)
        return(df)
    
    def fit_transform(self, df):

        self.fit(df)
        df_ = self.transform(df)

        return df_

    def inverse_transform(self, df):
        results = list()
        for key, data in df.to_dict().items():
            data = np.array(list(data.values())).reshape((-1, 1))
            scaled_data = self.scalers[key].inverse_transform(data).flatten()
            results.append(scaled_data)

        df = pd.DataFrame(np.array(results).T, columns=df.columns)
        return(df)

def set_snowflake_info():
    parser = argparse.ArgumentParser(description="Set Snowflake connection parameters.")

    parser.add_argument("--region_name", type=str, default="us-west-2", help="AWS region where the secret is stored")
    parser.add_argument("--secrets_name", type=str, default="AmazonSageMaker-DataWranglerSnowflakeCreds", help="Name of the Secrets Manager entry")
    parser.add_argument("--role", type=str, default="SAGEMAKER_DSCI_TEST", help="IAM role for Snowflake access")
    parser.add_argument("--warehouse", type=str, default="READER_WH", help="Snowflake virtual warehouse")
    parser.add_argument("--database", type=str, default="ENTERPRISEDATALAKE_PROD", help="Snowflake database")
    parser.add_argument("--schema", type=str, default="DEV", help="Snowflake schema")
    parser.add_argument("--table", type=str, default="V_EDR_ACTUAL_SURVEY", help="Table to query from Snowflake")

    # Parse only known args to avoid conflict in environments like Jupyter
    args, _ = parser.parse_known_args()
    return args
