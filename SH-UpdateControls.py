
#!/usr/bin/env python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import boto3
import logging
import re
import argparse
import time
import utils
import json
from datetime import datetime
from collections import OrderedDict
from botocore.exceptions import ClientError
from botocore.exceptions import ProfileNotFound
from botocore.exceptions import NoCredentialsError

LOG_FILENAME = datetime.now().strftime('logfile_%H_%M_%S_%d_%m_%Y.log')
for handler in logging.root.handlers[:]:
      logging.root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s - %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', datefmt='%d-%b-%y %H:%M:%S',filename=LOG_FILENAME,level=logging.INFO)    
logging.info('Initializing Update control script')



def assume_role(profile, aws_account_number, role_name):
    """
    Assumes the provided role in each account and returns a SecurityHub client
    :param aws_account_number: AWS Account Number
    :param role_name: Role to assume in target account
    :param aws_region: AWS Region for the Client call, not required for IAM calls
    :return: SecurityHub client in the specified AWS Account and Region
    """
     # Beginning the assume role process for account
    try :
        if profile:
            session = boto3.session.Session(profile_name=profile)
            sts_client = session.client('sts')
        else :
            sts_client = boto3.client('sts')
    except ProfileNotFound as ie:
        print("Exception : {0}".format(ie))
        logging.error("AWS CLI Configure profile  {} could not be found".format(profile))
        quit()    
    except NoCredentialsError as ie:
        print("Exception : {0}".format(ie))
        logging.error("Missing deafult profile please verify the AWS CLI credentails and config file")
        quit()
    # Get the current partition
    partition = sts_client.get_caller_identity()['Arn'].split(":")[1]
    
    response = sts_client.assume_role(
        RoleArn='arn:{}:iam::{}:role/{}'.format(
            partition,
            aws_account_number,
            role_name
        ),
        RoleSessionName='RoleAssumedBy-SecurityHub-UpdateControl-Script'
    )
    
    # Storing STS credentials
    session = boto3.Session(
        aws_access_key_id=response['Credentials']['AccessKeyId'],
        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
        aws_session_token=response['Credentials']['SessionToken']
    )

    print("Assumed session for {}.".format(
        aws_account_number
    ))

    return session



if __name__ == '__main__':
    
    # Setup command line arguments
    parser = argparse.ArgumentParser(description='Update SecurityHub controls')
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument('--input-file', type=argparse.FileType('r'), help='Path to CSV file containing the list of account IDs')
    required.add_argument('--assume-role', type=str, required=True, help="Role name of the execution role in each account")
    required.add_argument('--regions', type=str, required=True, help="comma separated list of regions to update SecurityHub controls. Specify ALL for considering all available regions disabled")
    required.add_argument('--standard', type=str, required=True,help="enter the standard code (CIS or PCIDSS or AFSBP for more info refer https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-standards.html")
    required.add_argument('--control-id-list', type=str, required=True,help="comma separated list of controls, example for CIS enter -  (1.1,1.2) for PCIDSS enter - (PCI.AutoScaling.1,PCI.CloudTrail.4) )")
    required.add_argument('--control-action', type=str, required=True,help="For enabling controls use ENABLED for disabling use DISABLED")
    required.add_argument('--disabled-reason', type=str, help="Reason for disabling the controls. This arguement is NOT required if you are enabling controls")
    optional.add_argument('--profile', type=str, help="AWS CLI named profile to be used in the script. Make sure the credentials in this profile have permissions to assume the execution role in each account. If you do not use this argument the default profile will be used")
    optional.add_argument('--regions-exception', type=str, help="AWS CLI named profile to be used in the script. Make sure the credentials in this profile have permissions to assume the execution role in each account. If you do not use this argument the default profile will be used")
    parser._action_groups.append(optional)
    args = parser.parse_args()
    accountslist=[]

    failed_accounts = []
    successful_accounts= []

    try:

        standard_code=args.standard.upper()
        control_update_action=args.control_action.upper()
        
        if(control_update_action == 'DISABLED' or control_update_action == 'ENABLED'):
            if control_update_action == 'DISABLED' :
                if args.disabled_reason:
                    disabled_reason=args.disabled_reason
                else: 
                    print("\nError : Supply paramater --disabled-reason while update action is DISABLED")
                    logging.error("Supply paramater --disabled-reason while update action is DISABLED")
                    quit()
        else:
            print("\nError : --control-action should be either DISABLED or ENABLED, value {} is invalid".format(control_update_action))
            logging.error("--control-action should be either DISABLED or ENABLED, value {} is invalid".format(control_update_action))
            quit()
        control_ids_list = [str(item) for item in args.control_id_list.split(',')]
    except IndexError as ie:
        print("Exception : {0}".format(ie))


    # Validating AWS Account numbers in csv file
    
    for account in args.input_file.read().splitlines():
      account=account.replace(" ", "") 
      if account.strip():
        if not re.match(r'[0-9]',account):
            print("\nError : Validation failed, invalid charater detected in AWS account number {}, please verify accounts csv file".format(account))
            logging.error("Validation failed, invalid charater detected in AWS account number {}, please veirfy the account csv file".format(account))
            quit()
        if(len(account)!=12):
            print("\nError : Validation failed, invalid digits in AWS Account number {}".format(account))
            logging.error("Validation failed, AWS account number {} is not 12 digits long".format(account))
            quit()
        accountslist.append(account)
        print("AWS Account # {} is valid".format(account))

    
    if args.profile:
        profile= args.profile
    else :
        profile= None
  # Getting SecurityHub regions
    session = boto3.session.Session() 
    try:
        if profile:
            session = boto3.session.Session(profile_name=profile)
            print("Using profile {} ".format(profile))
            logging.info("Using AWS CLI Configure profile {} ".format(profile))
            
        else: 
            print("Using default aws cli profile")
            logging.info("Using default AWS CLI Configure profile")
    except ProfileNotFound as ie:
        print("Exception : {0}".format(ie))
        logging.error("AWS CLI Configure profile  {} could not be found".format(profile))
        quit()
    except NoCredentialsError as ie:
        print("Exception : {0}".format(ie))
        logging.error("Missing deafult profile please verify the AWS CLI credentails and config file")
        quit()

    securityhub_regions = []
    
    if args.regions == 'ALL':
            securityhub_regions = session.get_available_regions('securityhub')
            if args.regions_exception:
                securityhub_regions_exceptions = [str(item) for item in args.regions_exception.split(',')]
                invalid_sh_regions_exception = list(set(securityhub_regions_exceptions).difference(securityhub_regions))

                if invalid_sh_regions_exception:
                    print("\nError: Invalid Security Hub exception region(s) {}".format(invalid_sh_regions_exception))
                    logging.error("Invalid Security Hub exception region(s) {}".format(invalid_sh_regions_exception))
                    quit()
                
                for region in securityhub_regions_exceptions:
                    securityhub_regions.remove(region)
    else :
            securityhub_regions = [str(item) for item in args.regions.split(',')]
            all_securityhub_regions = session.get_available_regions('securityhub')
            invalid_sh_regions = list(set(securityhub_regions).difference(all_securityhub_regions))
            if invalid_sh_regions:
                print("\nError: Invalid Security Hub region(s) {}".format(invalid_sh_regions))
                logging.error("Invalid Security Hub region(s) {}".format(invalid_sh_regions))
                quit()


    for account in accountslist:
        print("==========================================")
        try:
            session = assume_role(profile, account, args.assume_role)
            for aws_region in securityhub_regions:
                print('Beginning with {account} in {region}'.format(
                   account=account,
                    region=aws_region
                ))

                
                sh_client = session.client('securityhub', region_name=aws_region)


                for control_id in control_ids_list:
                    try:
                        control_arn=utils.get_control_arn_for_standard(aws_region,account,control_id,standard_code)
                        if(control_update_action == 'DISABLED'):
                            response = sh_client.update_standards_control(
                                StandardsControlArn=control_arn,
                                ControlStatus='DISABLED',
                                DisabledReason='"Disabled for testing"'
                            )
                            if(response['ResponseMetadata']['HTTPStatusCode']==200):
                                print("\nSuccessfully DISABLED control "+ control_arn )
                                logging.info("Successfully DISABLED control "+ control_arn )
                                successful_accounts.append(control_update_action + "  --->  "+ control_arn)
                            else :
                                print(response) 

                        if(control_update_action == 'ENABLED'):
                            response = sh_client.update_standards_control(
                                StandardsControlArn=control_arn,
                                ControlStatus='ENABLED'
                            )
                            if(response['ResponseMetadata']['HTTPStatusCode']==200):
                                print("\nSuccessfully ENABLED control "+ control_arn )
                                logging.info("Successfully ENABLED control "+ control_arn )
                                successful_accounts.append(control_update_action + "  --->  "+ control_arn)
                            else:
                                print(response) 
                    except ClientError as e:
                            print("\nError updating control in {}   {}  for  {}".format(account,aws_region,control_arn))
                            logging.error("Unable to update control in {}   {} for  {}".format(account,aws_region,control_arn))
                            print(e)
                            
                            failed_accounts.append(
                               account + " | "+repr(e) + " | " + " | "+ control_arn + " | " + aws_region
                            )

        except ClientError as e:
            print("\nError processing Account {}".format(account))
            logging.error("Could not process Account {}".format(account))
            print(e)
            failed_accounts.append({
                  account + " | "+ repr(e)
            })
    print("---------------------------------------------------------------")
    logging.info("---------------------------------------------------------------")
    print("\n")
    print("Execution Summary")
    logging.info("Execution Summary")
    print("Completed with {} successful control updates and {} failures".format(len(successful_accounts),len(failed_accounts)))
    logging.info("Completed with {} successful control updates and {} failures".format(len(successful_accounts),len(failed_accounts)))
    print("\n")
    print("---------------------------------------------------------------")
    logging.info("---------------------------------------------------------------")
    if len(successful_accounts) > 0:
        print("---------------------------------------------------------------")
        logging.info("---------------------------------------------------------------")
        print("Following {} Controls were {} ".format(len(successful_accounts),control_update_action))
        logging.info("Following {} Controls were {} ".format(len(successful_accounts),control_update_action))
        print("---------------------------------------------------------------")
        logging.info("---------------------------------------------------------------")
        for success_control in successful_accounts:
            print(success_control)
            logging.info(success_control)
        print("---------------------------------------------------------------")
        logging.info("---------------------------------------------------------------")
    if len(failed_accounts) > 0:
        print("---------------------------------------------------------------")
        logging.info("---------------------------------------------------------------")
        print("{} failures".format(len(failed_accounts)))
        logging.info("{} failures".format(len(failed_accounts)))
        print("---------------------------------------------------------------")
        logging.info("---------------------------------------------------------------")
        for account in failed_accounts:
            print(account)
            logging.error(account)
        print("---------------------------------------------------------------")
        logging.info("---------------------------------------------------------------")