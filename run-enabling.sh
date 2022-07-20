#!/bin/bash

python SH-UpdateControls.py \
--input-file accounts.csv \
--assume-role ManageSecurityHubControlsExecutionRole \
--regions 'us-west-2' \
--standard CIS \
--control-id-list 1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10,1.11,1.12,1.13,1.16,1.20,1.22 \
--control-action ENABLED 

176632934028

python SH-UpdateControls.py \
--input-file accounts.csv \
--assume-role ManageSecurityHubControlsExecutionRole \
--regions 'us-west-2' \
--standard CIS \
--control-id-list 1.11 \
--control-action ENABLED 