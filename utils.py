def get_control_arn_for_standard(region, accountid,control, standard):
    if standard == "CIS1.2":
        return 'arn:aws:securityhub:{region}:{accountid}:control/cis-aws-foundations-benchmark/v/1.2.0/{control}'.format( region=region,accountid=accountid, control=control)
    if standard == "CIS1.4":
        return 'arn:aws:securityhub:{region}:{accountid}:control/cis-aws-foundations-benchmark/v/1.4.0/{control}'.format( region=region,accountid=accountid, control=control)
    if standard == "NIST-800-53":
        return 'arn:aws:securityhub:{region}:{accountid}:control/nist-800-53/v/5.0.0/{control}'.format( region=region,accountid=accountid, control=control)
    if standard == "PCIDSS":
        return 'arn:aws:securityhub:{region}:{accountid}:control/pci-dss/v/3.2.1/{control}'.format( region=region,accountid=accountid, control=control)
    if standard == "AFSBP":
        return 'arn:aws:securityhub:{region}:{accountid}:control/aws-foundational-security-best-practices/v/1.0.0/{control}'.format( region=region,accountid=accountid, control=control)
    return 'INVALID_STANDARD'