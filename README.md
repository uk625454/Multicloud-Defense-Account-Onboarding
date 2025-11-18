In the sample python folder provided, the descriptions of the most relevant files are as follows: 

aws-account-onboard.py

This file contains a function (aws_flow() ) that can be used to onboard AWS accounts into the multicloud defense controller after the StackSet is used to deploy the CFT into the appropriate accounts.  

enable-inventory.py

This file contains a function (enable_inventory_flow() ) that can be used to enable the region in which you would like to discover AI assets (for a given account). Note, this function has to be called each time you would like to add a new region for asset discovery for a given account. 

To run the files in the sample python folder, you can take the following steps inside the folder after you have populated the variables for the two files mentioned above:

python3 -m venv mcd

source mcd/bin/activate

pip install requests

python onboard-aws-account.py

python enable-inventory.py


Additional Caveats

An external ID is required for the CFT. This external ID can be generated once from multicloud defense controller UI and then used in the CFT and in the python file for multicloud defense account onboarding. 

<img width="468" height="251" alt="image" src="https://github.com/user-attachments/assets/7743b5d8-c54f-468c-821f-cafaa48f8c55" />

