## AWS Security Hub Bulk Enable or Disable Controls Scripts

This script helps in enabling or disabling Security Hub controls in multiple accounts and in multiple security hub supported regions.

## License Summary

This sample code is made available under a modified MIT license. See the LICENSE file.

## Prerequisites

* The scripts depend on a pre-existing role in the central account and all of the member accounts that will be linked, the role name must be the same in all accounts and the role trust relationship needs to allow your instance or local credentials to assume the role.  The policy document below contains the required permission for the script to succeed:

``` 
{
    "Version": "2012-10-17",
    "Statement": [
        
        {
            "Action": "securityhub:UpdateStandardsControl",
            "Resource": "*",
            "Effect": "Allow"
        }
    ]
}
```
If you do not have a common role that includes at least the above permission you will need to create a role in each member account as well as the master account with at least the above permission.  When creating the role ensure you use the same role name in every account.  You can use the aws-securityhub-disablecontrols-executionrole.yml CloudFormation Template to automate this process, as the template creates only global resources it can be created in any region. Utilize Cloudformation stack sets to instantiate the cloudformation stacks in multiple accounts.


* A CSV file that includes the list of accounts.  Accounts should be listed one per line in the format of AccountId.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

