==========================
Using Emily with AWS Alexa
==========================

Emily can run inside of AWS Lambda and serve as a chatbot endpoint for Alexa to communicate with.

Tools and Requirements
======================

- Pip
- Python 2.7
- AWS Developer Account
- AWS Account

Instructions
============

1. In AWS create a new DynamoDB table to hold Emily's session variables.

- Table Name: emily_session_vars (or whatever your preference is)
- Primary Key: session_id (Number)

2. Create an application directory locally

.. code-block:: bash

    $ mkdir emily_alexa_lambda
    $ cd emily_alexa_lambda

3. Copy the lambda_function.py template from emily/templates/aws_alexa_lambda into the new directory.

4. Open the template in a text editor and replace <your_dynamodb_table_here> with the name of your DynamoDB table.

- You can also change the region if necessary. Default is 'us-east-1'

5. Install emily and her dependecies locally in your application directory using pip

.. code-block:: bash

    $ pip install -t . emily[aws]

6. Zip the contents of the application directory

.. code-block:: bash

    $ zip -r emily_alexa_lambda_v1.zip .

7. In AWS create a new Lambda with the following settings

- Template: Blank Function
- Configure Triggers: Alexa Skills Kit
- Name: emily_alexa_lambda
- Runtime: Python 2.7
- Code Entry Type: Upload a .ZIP file
- Upload your zip file: emily_alexa_lambda_v1.zip
- Handler: lambda_function.lambda_handler (this is the default)
- Role: Create a Custom Role (opens new window)

  - IAM Role: Create a new IAM role
  - Role Name: emily_lambda_execution
  - Allow

- Advanced Settings:

  - Timeout: 15 Seconds

- Next
- Create Function

8. Copy the ARN of the new Lambda (will be needed later)

9. Add DynamoDB privileges to new IAM Role

- `AWS Documentation <http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/using-identity-based-policies.html>`_

10. Log onto `AWS Developer Portal <https://developer.amazon.com/>`_

- Create an account if you don't already have one (note that this is different from your AWS account)

11. Once logged in, open the Alexa tab and select 'Alexa Skills Kit'

12. Select 'Add a New Skill'

- Name: Emily
- Invocation Name: emily
- Audio Player: No
- Next

- Intent Schema: See intent_schema.json
- Custom Slot Types:

  - Add Slot Type
  - Enter Type: CATCH_ALL
  - Enter Values: See custom_slot_type_values.txt
  - Add

- Sample Utterances: See sample_utterances.txt
- Save
- Next

- Service Endpoint Type: AWS Lambda ARN (Amazon Resource Name)
- Geographical Region: North America
- ARN: The ARN of the Lambda you copied from in step 8
- Account Linking: No
- Next

- Test with: tell Emily hello