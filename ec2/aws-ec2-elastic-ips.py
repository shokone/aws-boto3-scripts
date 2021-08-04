#!/usr/bin/env python3

# 
# Purpose :     Work with elastic ips
# Author:       Ivan Martinez
# Dependencies: python3, boto3, Aws cli
#

import boto3
from botocore.exceptions import ClientError
import sys
import argparse
import json


## First create arguments to work with them
argparser = argparse.ArgumentParser(description='Perform common instance tasks')
argparser.add_argument('action', help='Instance action to be performed list/add/associate/disassociate/release')
argparser.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
argparser.add_argument('-r', '--region', default="all", help='Default is all, or provide as argument')
argparser.add_argument('-e', '--allocationid', default="null", help='ID of Aws Elastic IP')
argparser.add_argument('-i', '--instanceid', default="null", help='ID of Aws EC2 Instance')
argparser.add_argument('-a', '--associationid', default="null", help='ID of Aws Elastic IP Association')
argparser.add_argument('-t', '--tags', help='Tags to add to a new Aws Elastic IP. Ej:\'[{"Key":"string","Value":"string"}]\'')


try:
    args = argparser.parse_args()
    print ("[INFO] Performing action: ", args.action)
    print ("[INFO] Profile : ", args.profile)
    print ("[INFO] Region : ", args.region )
    print ("[INFO] Elastic IP Allocation ID: ", args.allocationid, "\n")
except:
    print ("Please run -h for help, Action and Region are mandatory arguments except for list.")
    sys.exit(1)


## set ec2 client
def setEc2client(regionName):
    try:
        global ec2client
        ec2client = boto3.client('ec2', region_name=regionName)
        
    except:
        print("[ERROR] Failed to set ec2client, please ensure arguments are passed.")
        sys.exit(1)


## set ec2 client whitout region
def setEc2Emptyclient():
    try:
        global ec2client
        ec2client = boto3.client('ec2')
        
    except:
        print("[ERROR] Failed to set ec2client, please ensure arguments are passed.")
        sys.exit(1)


def checkEipId(eipid):
    if secgroup == "null":
        print("[ERROR] Elastic IP Allocation ID must be provided as argument.")
        sys.exit(1)


def checkRegion(region):
    if region == "all":
        print("[ERROR] Region must be provided as argument.")
        sys.exit(1) 


## Get info of all security groups in selected region
def describeElasticIPs(region, eips):
    for eip in eips['Addresses']:
        eipallocationid     = eip.get("AllocationId")
        eippublicip = eip.get("PublicIp")
        eipdomain = eip.get("Domain")
        eipassociationid     = eip.get("AssociationId")
        eipinstanceid = eip.get("InstanceId")
        eipifaceid = eip.get("NetworkInterfaceId")
        eipprivateip = eip.get("PrivateIpAddress")
        
        try:
            for tags in eip['Tags']:
                if tags['Key'] == 'Name':
                    eipName = tags.get('Value')
        except:
            eipName = "Undefined"
        
        try:
            print("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" %(region, eipName, eipallocationid, eippublicip, eipdomain, eipassociationid, eipinstanceid, eipifaceid, eipprivateip))
        except:
            print("[ERROR] Failed to get security groups information.")


def main():
	## setting some global variables so that it can be reused
    global ec2client
    global profile
    global region

    profile = args.profile
    region = args.region

    ## First set aws profile
    boto3.setup_default_session(profile_name=profile)

    setEc2client(region)

    if args.action != "list":
        checkRegion(region)
        setEc2client(region)

    if args.action == "list":
        print("[INFO] Listing Elastic IPs...")
        print("Region\t\tName\tAllocation ID\tPublic IP\tDomain\tAssociation ID\tInstance ID\tIface ID\tPrivate IP")

        setEc2Emptyclient()
        regions = ec2client.describe_regions()['Regions']

        for reg in regions:
            region = reg['RegionName']
            setEc2client(region)
            elasticIPs = ec2client.describe_addresses()
            describeElasticIPs(region, elasticIPs)

        sys.exit(0)

    elif args.action == "add":
        print("[INFO] Allocating new Elastic IP... ")
        tags = json.loads(args.tags)

        try:
            eip = ec2client.allocate_address(Domain='vpc')
            ec2client.create_tags(
                Resources=[eip["AllocationId"]],
                Tags=tags
            )
            print("[INFO] Allocating Elastic IP succesfully requested")
            print("[INFO] Region:        %s" %(region))
            print("[INFO] Allocation ID: %s" %(eip["AllocationId"]))
            print("[INFO] Public IP:     %s" %(eip["PublicIp"]))
        except ClientError as e:
            print(e)

        sys.exit(0)

    elif args.action == "associate":
        print("[INFO] Associating Elastic IP %s with instance %s... " %(args.allocationid, args.instanceid))
        try:
            eip = ec2client.associate_address(AllocationId=args.allocationid,InstanceId=args.instanceid)
            print("[INFO] Associate Elastic IP with association id %s succesfully." %(eip["AssociationId"]))
        except ClientError as e:
            print(e)
        sys.exit(0)

    elif args.action == "disassociate":
        print("[INFO] Disassociating Elastic IP with association id %s... " %(args.associationid))
        try:
            ec2client.disassociate_address(AssociationId=args.associationid)
            print("[INFO] Disassociate Elastic IP with association id %s succesfully." %(args.associationid))
        except ClientError as e:
            print(e)
        sys.exit(0)

    elif args.action == "release":
        print("[INFO] Release Elastic IP %s... " %(args.allocationid))
        try:
            ec2client.release_address(AllocationId=args.allocationid)
            print("[INFO] Release Elastic IP %s succesfully." %(args.allocationid))
        except ClientError as e:
            print(e)
        sys.exit(0)


if __name__ == "__main__":
    main()
