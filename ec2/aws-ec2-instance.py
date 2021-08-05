#!/usr/bin/env python3

# 
# Purpose :     Perform basic instance tasks using python and boto3
# Author:       Ivan Martinez
# Dependencies: python3, boto3, Aws cli
#


import boto3
from botocore.exceptions import ClientError
import sys
import argparse
import logging

## add default logger config
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)

## First create arguments to work with them
argparser = argparse.ArgumentParser(description='Perform common instance tasks')
argparser.add_argument('action', help='Instance action to be performed list/start/stop/status')
argparser.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
argparser.add_argument('-r', '--region', default="all", help='Default is all, or provide as argument')
argparser.add_argument('-i', '--instance', default="null", help='ID of Aws instance')


try:
    args = argparser.parse_args()
    logging.info("Performing action: %s" %(args.action))
    logging.info("Profile:           %s" %(args.profile))
    logging.info("Region:            %s" %(args.region))
    logging.info("Instance ID:       %s\n" %(args.instance))
except:
    logging.error("Please run -h for help, Action and Region are mandatory arguments except for list.")
    sys.exit(1)



## set ec2 client
def setEc2client(regionName):
    try:
        global ec2client
        ec2client = boto3.client('ec2', region_name=regionName)
        
    except:
        logging.error("Failed to set ec2client, please ensure arguments are passed.")
        sys.exit(1)


## set ec2 client whitout region
def setEc2Emptyclient():
    try:
        global ec2client
        ec2client = boto3.client('ec2')
        
    except:
        logging.error("Failed to set ec2client, please ensure arguments are passed.")
        sys.exit(1)


def checkInstanceID(instance):
    if instance == "null":
        logging.error("Instance ID must be provided as argument.")
        sys.exit(1)


def checkRegion(region):
    if region == "all":
        logging.error("Region must be provided as argument.")
        sys.exit(1) 


## Get info of all instances in selected region
def describeInstances(region, instances):
    for data in instances['Reservations']:
        for instance in data['Instances']:
            iid        = instance.get("InstanceId", "NULL")
            itype      = instance.get("InstanceType", "NULL")
            istatus    = instance.get('State').get('Name')
            iprivateip = instance.get("PublicIpAddress", "NULL")
            ipublicip  = instance.get("PrivateIpAddress", "NULL")
            ## now get tag name of instance
            for tags in instance['Tags']:
                if tags['Key'] == 'Name':
                    iName = tags.get('Value', "NULL")
                try: iName
                except: iName = "Undefined"

            try:
                print("%s\t%s\t%s\t%s\t%s\t%s\t%s" %(region, iName, iid, itype, istatus, iprivateip, ipublicip))
            except:
                logging.error("Failed to get instance information.")


## Start instance
def startInstance(instance):
    try:
        ec2client.start_instances(InstanceIds=[instance])
        logging.info("Starting instance %s. Please wait to be ready." %(instance))
        waiter = ec2client.get_waiter('system_status_ok')
        waiter.wait(InstanceIds=[instance])
        logging.info("Instance %s is ready" %(instance))
    except:
        logging.error("Failed to start instance %s" %(instance))


## Stop instance
def stopInstance(instance):
    try:
        ec2client.stop_instances(InstanceIds=[instance])
        logging.info("Stopping instance %s. Please wait to be ready." %(instance))
        waiter = ec2client.get_waiter('instance_stopped')
        waiter.wait(InstanceIds=[instance])
        logging.info("Instance %s stopped" %(instance))
    except:
        logging.error("Failed to stop instance %s" %(instance))


## Get instance status
def statusInstance(instance):
    for data in instance['Reservations']:
        for instance in data['Instances']:
            iid        = instance.get("InstanceId", "NULL")
            istatus    = instance.get('State').get('Name')
            ## now get tag name of instance
            for tags in instance['Tags']:
                if tags['Key'] == 'Name':
                    iName = tags.get('Value', "NULL")
                try: iName
                except: iName = "Undefined"

            try:
                logging.info("Instance %s with ID %s is %s" %(iName, iid, istatus))
            except:
                logging.error("Failed to get instance status.")


def main():
    ## setting some global variables so that it can be reused
    global ec2client
    global profile
    global region

    profile = args.profile
    region = args.region

    ## First set aws profile
    boto3.setup_default_session(profile_name=profile)
    
    ## load region passed in arguments if action is not list
    if args.action != "list":
        checkRegion(region)
        setEc2client(region)

    if args.action == "list":
        logging.info("Listing instances...")
        print("Region\tName\tID\tType\tStatus\tPrivate IP\tPublic IP")

        setEc2Emptyclient()
        try:
            regions = ec2client.describe_regions()['Regions']
        except ClientError as e:
            logging.error(e)

        for reg in regions:
            region = reg['RegionName']
            setEc2client(region)
            instances = ec2client.describe_instances()
            describeInstances(region, instances)

        sys.exit(0)

    elif args.action == "start":
        checkInstanceID(args.instance)
        logging.info("Starting instance... ", args.instance)
        startInstance(args.instance)
        sys.exit(0)

    elif args.action == "stop":
        checkInstanceID(args.instance)
        logging.info("Stoping instance... ", args.instance)
        stopInstance(args.instance)
        sys.exit(0)

    elif args.action == "status":
        checkInstanceID(args.instance)
        logging.info("Checking status of instance %s... ", args.instance)
        
        try:
            instance = ec2client.describe_instances(InstanceIds=[args.instance])
        except ClientError as e:
            logging.error(e)
            
        statusInstance(instance)
        sys.exit(0)


if __name__ == "__main__":
    main()
