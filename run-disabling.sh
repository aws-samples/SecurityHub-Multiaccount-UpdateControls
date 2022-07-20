#!/bin/bash

python SH-UpdateControls.py \
--input-file accounts.csv \
--assume-role ManageSecurityHubControlsExecutionRole \
--regions ALL \
--standard CIS \
--control-id-list 1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10,1.11,1.12,1.13,1.16,1.20,1.22 \
--control-action DISABLED \
--disabled-reason 'Disabling redundant control for IAM.' \
--regions-exception 'us-west-2'



python SH-UpdateControls.py \
--input-file accounts.csv \
--assume-role ManageSecurityHubControlsExecutionRole \
--regions ALL \
--standard CIS \
--control-id-list 1.14 \
--control-action DISABLED \
--disabled-reason 'Not applicable,The key holders of root accounts are located in different geographical locations, making Hardware MFA management complicated.'


# disabling AFSBP for AWS Foundational Security Best Practices
python SH-UpdateControls.py \
--input-file accounts.csv \
--assume-role ManageSecurityHubControlsExecutionRole \
--regions ALL \
--standard AFSBP \
--control-id-list IAM.6 \
--control-action DISABLED \
--disabled-reason 'Not applicable,The key holders of root accounts are located in different geographical locations, making Hardware MFA management complicated.' 