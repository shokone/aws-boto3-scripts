# aws-boto3-scripts

Python scripts for AWS using boto3 SDK

## Install

### Requirements
Python 3.4 or above and [boto3](https://github.com/boto/boto3)

### Install
Execute `pip3 install -r requirements.txt`

```shell
git clone https://github.com/shokone/aws-boto3-scripts.git
cd aws-boto3-scripts
pip install -r requirements.txt
```

### Usage

```shell
$ python3 ec2/aws-ec2-instance.py -h
usage: aws-ec2-instance.py [-h] [-p PROFILE] [-r REGION] [-i INSTANCE] action

Perform common instance tasks

positional arguments:
  action                Instance action to be performed list/start/stop/status

optional arguments:
  -h, --help            show this help message and exit
  -p PROFILE, --profile PROFILE
                        If no profile provided, assumes default
  -r REGION, --region REGION
                        Default is all, or provide as argument
  -i INSTANCE, --instance INSTANCE
                        ID of Aws instance
Please run -h for help, Action and Region are mandatory arguments except for list.

```


```shell
$ python3 ec2/aws-ec2-security-groups.py -h
usage: aws-ec2-security-groups.py [-h] [-p PROFILE] [-r REGION] [-i SECGROUPID] action

Perform common instance tasks

positional arguments:
  action                Instance action to be performed list/rules

optional arguments:
  -h, --help            show this help message and exit
  -p PROFILE, --profile PROFILE
                        If no profile provided, assumes default
  -r REGION, --region REGION
                        Default is all, or provide as argument
  -i SECGROUPID, --secgroupid SECGROUPID
                        ID of Aws security group
Please run -h for help, Action and Region are mandatory arguments except for list.

```