#!/usr/bin/env python3

# 
# Purpose :     Get Information of security groups
# Author:       Ivan Martinez
# Dependencies: python3, boto3, Aws cli
#

import boto3
from botocore.exceptions import ClientError
import sys
import argparseimport logging

## add default logger config
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)

## First create arguments to work with them
argparser = argparse.ArgumentParser(description='Perform common instance tasks')
argparser.add_argument('action', help='Instance action to be performed list/rules')
argparser.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
argparser.add_argument('-r', '--region', default="all", help='Default is all, or provide as argument')
argparser.add_argument('-i', '--secgroupid', default="null", help='ID of Aws security group')

try:
    args = argparser.parse_args()
    logging.info("Performing action: %s" %(args.action))
    logging.info("Profile:           %s" %(args.profile))
    logging.info("Region:            %s" %(args.region))
    logging.info("Security Group ID: %s\n" %(args.secgroupid))
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


def checkSGID(secgroup):
    if secgroup == "null":
        logging.error("Security group ID must be provided as argument.")
        sys.exit(1)


def checkRegion(region):
    if region == "all":
        logging.error("Region must be provided as argument.")
        sys.exit(1) 


## Get info of all security groups in selected region
def describeSecurityGroups(region, secgroups):
    for secgroup in secgroups['SecurityGroups']:
        sgid        = secgroup.get("GroupId", "NULL")
        sgVPCid     = secgroup.get("VpcId", "NULL")
        sgName      = secgroup.get('GroupName')

        try:
            print("%s\t%s\t%s\t%s" %(region, sgName, sgid, sgVPCid))
        except:
            logging.error("Failed to get security groups information.")


def describeSecurityGroupRules(region, secgroups):
	for secgroup in secgroups['SecurityGroups']:
		sgName = secgroup.get('GroupName')

		logging.info("Getting inbound rules for Security Group %s" %(sgName))
		print("Protocol\tFrom Port\tTo Port\tCidr\t\tDescription")

		for inbound in secgroup['IpPermissions']:
			from_port = inbound.get("FromPort", "NULL")
			protocol  = inbound.get("IpProtocol", "NULL")
			to_port   = inbound.get("ToPort", "NULL")
			
			for ipr in inbound['IpRanges']:
				cidr_ip = ipr.get("CidrIp")
				desc    = ipr.get("Description")
				print("%s\t\t%s\t\t%s\t%s\t%s" %(protocol, from_port, to_port, cidr_ip, desc))

			for ip6r in inbound['Ipv6Ranges']:
				cidr_ip = ipr.get("CidrIp")
				desc    = ipr.get("Description")
				print("%s\t%s\t%s\t%s\t%s" %(protocol, from_port, to_port, cidr_ip, desc))

		logging.info("Getting outboud rules for Security Group %s" %(sgName))
		print("Protocol\tFrom Port\tTo Port\tCidr\t\tDescription")

		for outbound in secgroup['IpPermissionsEgress']:
			from_port = outbound.get("FromPort", "NULL")
			protocol  = outbound.get("IpProtocol", "NULL")
			to_port   = outbound.get("ToPort", "NULL")

			for ipr in outbound['IpRanges']:
				cidr_ip = ipr.get("CidrIp")
				desc    = ipr.get("Description")
				print("%s\t\t%s\t\t%s\t%s\t%s" %(protocol, from_port, to_port, cidr_ip, desc))

			for ip6r in outbound['Ipv6Ranges']:
				cidr_ip = ipr.get("CidrIp")
				desc    = ipr.get("Description")
				print("%s\t%s\t%s\t%s\t%s" %(protocol, from_port, to_port, cidr_ip, desc))	



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
        logging.info("Listing Security Groups...")
        print("Region\t\tName\tID\tVPC")

        setEc2Emptyclient()
        try:
            regions = ec2client.describe_regions()['Regions']
        except ClientError as e:
            logging.error(e)
            
        for reg in regions:
            region = reg['RegionName']
            setEc2client(region)
            securityGroups = ec2client.describe_security_groups()
            describeSecurityGroups(region, securityGroups)

        sys.exit(0)

    elif args.action == "rules":
    	checkSGID(args.secgroupid)
    	logging.info("Listing rules of Security Group %s... " %(args.secgroupid))

        try:
    	   securityGroups = ec2client.describe_security_groups(GroupIds=[args.secgroupid])
    	except ClientError as e:
            logging.error(e)

        describeSecurityGroupRules(region, securityGroups)
    	sys.exit(0)


if __name__ == "__main__":
    main()
