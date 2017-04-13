======================================
Running Emily in AWS Elastic Beanstalk
======================================

Elastic Beanstalk is an AWS service that handles the creation of virtual servers (EC2s) and a load balancer (ELB) for you.
Note that depending on VPC configurations, these steps may vary.

Tools and Requirements
======================

- Pip
- Python 2.7
- AWS Account

Instructions
============

1. Create a local application directory

.. code-block:: bash

    $ mkdir emily_beanstalk
    $ cd emily_beanstalk

2. Copy application.py and requirements.txt from emily/templates/aws_beanstalk into your directory.

3. Open the applicaiton.py template in a text editor and replace <your_dynamodb_table_here> with the name of your DynamoDB table.

- You can also change the region if necessary. Default is 'us-east-1'

4. Create ebextensions directory and place emily_logs.config file in it

.. code-block:: bash

    $ mkdir .ebextensions

Note that this is a hidden folder. The emily_logs.config file tells Elastic Beanstalk to include Emily's logs with the rest of the Beanstalk logs.

5. Create a zip file for your application

.. code-block:: bash

    $ zip -r emily_beanstalk_v1.zip .

6. In AWS create an Elastic Beanstalk application with a name of your choosing.

7. Create a new environment within your application

- Environment Tier: Web server environment
- Select

- Preconfigured Environment: Python
- Upload your Code: Select your zip file

- Configure more options if needed (depends on your account and VPC setup)
or
- Create Environment

8. Once deployed, get the URL of your beanstalk environment

9. Attempt an HTTP GET against the URL plus the path "get_session" to get a new session

Example:

.. code-block:: bash

    $ curl http://emily-test.us-east-1.elasticbeanstalk.com/get_session
    40113

10. Attempt an HTTP POST against the URL plus the path "chat" with a message and session_id in the POST body

Example:

.. code-block:: bash

    $ curl -H "Content-Type: application/json" -X POST -d '{"session_id":40113,"message":"Hello"}' http://emily-test.us-east-1.elasticbeanstalk.com/chat
    {"response":"Hello!","session_id":40113}

Troubleshooting
===============

If you encounter errors with Emily running in Elastic Beanstalk, there are likely other configuration options that need to be set when creating the environment.
The best way to determine what changes need to be made is by looking at the last 100 log lines for errors.
Errors could include:
- Lack of IAM permissions
- Inaccessible instances due to VPC, Security Group, or Network ACL configurations