#!/usr/bin/python

import boto3
import yaml

with open('ec2_config.yaml', 'r') as stream:
    try:
        yamlconf = (yaml.safe_load(stream))
    except yaml.YAMLError as exc:
        print(exc)


ec2 = boto3.client('ec2')

ami_response = ec2.describe_images(
  Filters=[
        {
            'Name': 'description',
            'Values': [
                yamlconf['server']['description'],
            ]
        },
        {
            'Name': 'block-device-mapping.volume-type',
            'Values': [
                yamlconf['server']['ebs.volume_type'],
            ]
        },

        {
            'Name': 'name',
            'Values': [
                yamlconf['server']['ami_type'],
            ]
        },
        {
            'Name': 'owner-alias',
            'Values': [
                yamlconf['server']['owner_alias'],
            ]
        },
        {
            'Name': 'architecture',
            'Values': [
                yamlconf['server']['architecture'],
            ]
        },
        {
            'Name': 'virtualization-type',
            'Values': [
                yamlconf['server']['virtualization_type'],
            ]
        },
        {
            'Name': 'root-device-type',
            'Values': [
                yamlconf['server']['root_device_type'],
            ]
        },

    ],
)

ami_sorted = sorted(ami_response['Images'],
              key=lambda x: x['CreationDate'],
              reverse=True)
print('Your Image ID depends on the configuration file - ' + ami_sorted[0]['ImageId'])

user_data = str('#!/bin/bash\nyum update -y\nmkdir data\nmkfs -t xfs /dev/xvdf\nmount /dev/xvdf /data\nchgrp -R users /data\nchmod 770 /data\nuseradd -G users user1\nuseradd -G users user2\nmkdir -p /home/user1/.ssh\necho '+yamlconf['server']['users'][0]['ssh_key']+' > /home/user1/.ssh/authorized_keys\nmkdir -p /home/user2/.ssh\necho '+yamlconf['server']['users'][1]['ssh_key']+' > /home/user2/.ssh/authorized_keys\nchmod 700 /home/user1/.ssh && chmod 600 /home/user1/.ssh/authorized_keys\nchown -R user1:user1 /home/user1/.ssh\nchmod 700 /home/user2/.ssh && chmod 600 /home/user2/.ssh/authorized_keys\nchown -R user2:user2 /home/user2/.ssh')


response = ec2.run_instances(
    BlockDeviceMappings=[
        {
            'DeviceName': yamlconf['server']['volumes'][0]['device'],
            'Ebs': {

                'DeleteOnTermination': True,
                'VolumeSize': yamlconf['server']['volumes'][0]['size_gb'],
                'VolumeType': 'gp2'
            },
        },
        {
            'DeviceName': yamlconf['server']['volumes'][1]['device'],
            'Ebs': {

                'DeleteOnTermination': True,
                'VolumeSize': yamlconf['server']['volumes'][1]['size_gb'],
                'VolumeType': 'gp2'
            }
        },
    ],
    ImageId=ami_sorted[0]['ImageId'],
    InstanceType=yamlconf['server']['instance_type'],
    MinCount=yamlconf['server']['min_count'],
    MaxCount=yamlconf['server']['max_count'],
    UserData=user_data,
    Monitoring={
        'Enabled': False
    },
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'AutomationYAML'
                },
            ]
        },
    ],
)

ec2_instance = boto3.resource('ec2')
created_ec2 = ec2_instance.Instance(response['Instances'][0]['InstanceId'])
created_ec2.wait_until_running()
print(f"Instance is {created_ec2.state['Name']}")
iplook = ec2.describe_instances(
    InstanceIds=[
    created_ec2.instance_id,
    ],
)
print('Public DNS Name of your instance is ' + iplook['Reservations'][0]['Instances'][0]['PublicDnsName'])
print('Public IP of your instance is ' + iplook['Reservations'][0]['Instances'][0]['PublicIpAddress'])
