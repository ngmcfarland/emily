===========================
Running Emily in AWS Lambda
===========================

Emily can be deployed to the serverless architecture of Amazon Web Services using Lambda.

Tools and Requirements
======================

- Pip
- Python 2.7
- AWS Account

Instructions
============

1. In AWS create a new DynamoDB table to hold Emily's session variables.

- Table Name: emily_session_vars (or whatever your preference is)
- Primary Key: session_id (String)

2. Create an application directory locally

.. code-block:: bash

    $ mkdir emily_lambda
    $ cd emily_lambda

3. Copy the lambda_function.py template from emily/templates/aws_lambda into the new directory.

4. Open the template in a text editor and replace <your_dynamodb_table_here> with the name of your DynamoDB table.

- You can also change the region if necessary. Default is 'us-east-1'

5. Install emily and her dependecies locally in your application directory using pip

.. code-block:: bash

    $ pip install -t . emily[aws]

6. Zip the contents of the application directory

.. code-block:: bash

    $ zip -r emily_lambda_v1.zip .

7. In AWS create a new Lambda with the following settings

- Template: Blank Function
- Configure Triggers: None (can be added later)
- Name: emily_lambda
- Runtime: Python 2.7
- Code Entry Type: Upload a .ZIP file
- Upload your zip file: emily_lambda_v1.zip
- Handler: lambda_function.lambda_handler (this is the default)
- Role: Create a Custom Role (opens new window)

  - IAM Role: Create a new IAM role
  - Role Name: emily_lambda_execution
  - Allow

- Advanced Settings:

  - Timeout: 15 Seconds
  
- Next
- Create Function

8. Add DynamoDB privileges to new IAM Role

- `AWS Documentation <http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/using-identity-based-policies.html>`_

9. Configure test event for new Lambda

.. code-block:: json

  {
    "message": "hello"
  }

- Save and Test

10. Get session ID from Lambda response to use in future tests

.. code-block:: json

  {
    "message": "Tell me a pun",
    "session_id": 123
  }