#!/usr/bin/env python3

# 
# Purpose :     Get Information IAM users
# Author:       Ivan Martinez
# Dependencies: python3, boto3, Aws cli
#

import boto3
from botocore.exceptions import ClientError
import sys
import argparse
import logging
import textwrap

## add default logger config
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)

## First create arguments to work with them
argparser = argparse.ArgumentParser(description='Perform common instance tasks', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=textwrap.dedent('''\
    Additional information:
        list    -> show list of existing users
        details -> show details of selected user
    '''))
argparser.add_argument('action', help='Instance action to be performed list/details')
argparser.add_argument('-p', '--profile', default="default", help='If no profile provided, assumes default')
argparser.add_argument('-i', '--username', default="null", help='Name of Aws IAM User')

try:
    args = argparser.parse_args()
    logging.info("Performing action: %s" %(args.action))
    logging.info("Profile:           %s" %(args.profile))
    logging.info("User ID:           %s\n" %(args.username))
except:
    logging.error("Please run -h for help, Action and Region are mandatory arguments except for list.")
    sys.exit(1)


## set iam client
def setiamclient():
    try:
        global iamclient
        iamclient = boto3.client('iam')
        
    except ClientError as e:
        logging.error(e)
        sys.exit(1)


def checkUser(user):
    if user == "null":
        logging.error("Username must be provided as argument.")
        sys.exit(1)


## Get info of all users
def describeIAMUsers(users):
    for user in users['Users']:
        uid    = user.get("UserId")
        uname  = user.get("UserName")
        uarn   = user.get('Arn')
        ucdate = user.get("CreateDate")

        try:
            print("%s\t%s\t%s\t%s" %(uname, uid, uarn, ucdate))
        except:
            logging.error("Failed to get IAM Users information.")


def describeIAMUser(user):
    uid    = user["User"]["UserId"]
    uname  = user["User"]["UserName"]
    uarn   = user["User"]['Arn']
    ucdate = user["User"]["CreateDate"]

    print("Username:      %s" %(uname))
    print("ID:            %s" %(uid))
    print("ARN:           %s" %(uarn))
    print("Creation Date: %s" %(ucdate))
    print("Tags:")
    try: 
        user["User"]['Tags']
        for tag in user["User"]['Tags']:
            print("\t%s=%s" %(tag['Key'], tag['Value']))
    except:
        pass

    print("Permissions Boundary:")
    try: 
        user["User"]["PermissionsBoundary"]
        try:
            user["User"]["PermissionsBoundary"]['PermissionsBoundaryType']
            print("\t%s=%s" %(user["User"]["PermissionsBoundary"]['PermissionsBoundaryType'], user["User"]["PermissionsBoundary"]['PermissionsBoundaryArn']))
        except:
            pass

        try:
            for bound in user["User"]["PermissionsBoundary"]:
                print("\t%s=%s" %(bound['PermissionsBoundaryType'], bound['PermissionsBoundaryArn']))
        except:
            pass
            
    except:
        pass

def describeIAMGroups(groups):
    print("Groups:")
    for group in groups['Groups']:
        gname  = group.get("GroupName")
        garn   = group.get('Arn')

        try:
            print("\t%s=%s" %(gname, garn))
        except:
            logging.error("Failed to get IAM Users information.")

		
def describeIAMUserPolicies(user):
    print("Policies:")
    for policy in user['AttachedPolicies']:
        pname = policy.get("PolicyName")
        parn  = policy.get("PolicyArn")
        print("\t%s=%s" %(pname, parn))


def main():
	## setting some global variables so that it can be reused
    global iamclient
    global profile

    profile = args.profile

    ## First set aws profile
    boto3.setup_default_session(profile_name=profile)

    setiamclient()

    if args.action == "list":
        logging.info("Listing IAM users...")
        print("Name\tID\tARN\tCreation Date")

        try:
            iamusers = iamclient.list_users()
        except ClientError as e:
            logging.error(e)

        describeIAMUsers(iamusers)

        sys.exit(0)

    elif args.action == "details":
        checkUser(args.username)
        logging.info("Listing details of IAM User %s... " %(args.username))

        try:
            iamuser = iamclient.get_user(UserName=args.username)
            iampolicy = iamclient.list_attached_user_policies(UserName=args.username)
            iamgroups = iamclient.list_groups_for_user(UserName=args.username)
        except ClientError as e:
            logging.error(e)

        describeIAMUser(iamuser)
        describeIAMGroups(iamgroups)
        describeIAMUserPolicies(iampolicy)

        sys.exit(0)


if __name__ == "__main__":
    main()
