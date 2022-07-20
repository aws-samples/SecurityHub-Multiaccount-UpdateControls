#cd /homw/ec2-user
#sudo yum install git
#git clone https://github.com/BagheriReza/SecurityHub-Multiaccount-UpdateControls.git 

install:
	python3 -m venv SecurityHub-Multiaccount-UpdateControls/env
	source SecurityHub-Multiaccount-UpdateControls/env/bin/activate
	pip install pip --upgrade
	pip install boto3

init:
	cd /homw/ec2-user
	cd SecurityHub-Multiaccount-UpdateControls/
	source SecurityHub-Multiaccount-UpdateControls/env/bin/activate
	