# vm-deployment-aws
The script was tested on an EC2 Amazon Linux 2 AMI machine with a configured IAM user.

Environment: 
- Python 2.7.18
- boto3
- pyyaml
 
Use the following commands to install the required packages:  
`pip3 install --user boto3`

`pip3 install --user pyyaml`

1. Use `aws configure` to configure access key and default region for your IAM user. 
2. The script uses the default network parameters. Open port 22 with inbound rules in the default security group at same region as in point 1.

3. Copy files from current repository on your created EC2 machine.

`wget -P ~/ https://github.com/aeremin-it/vm-deployment-aws/archive/refs/heads/main.zip`

`unzip ~/main.zip`

4. Change the access permissions to users' private keys.

    `chmod 600 user1`

    `chmod 600 user2`
4. To generate new keys use `ssh-keygen -q -t rsa -C user1@localhost -f user1 -N ''` and `ssh-keygen -q -t rsa -C user2@localhost -f user2 -N ''` then replace public keys in the configuration file.
5. Run create_ec2.py with `python3 create_ec2.py` command. After the script finishes working, the public IP address will be displayed `PublicIP`. 
6. Then use `ssh -i user1 user1@PublicIP` or `ssh -i user2 user2@PublicIP` to connect as user1 and user2.
