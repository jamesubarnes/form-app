# Senior Developer Exercise

## Background

The purpose of this exercise is for us to get an understanding of both your technical skills, and how you go about planning and solving problems.

These tasks should only take 2-4 hours. You are welcome to use AI tools (e.g., Copilot, ChatGPT, Gemini) to assist with coding, documentation, or testing. If you do, please mention how you used them in your README.

You will be given Editor access to a blank GCP project. Please be mindful of resource usage—there is a budget cap of $100. If you reach this limit or if you have any issues accessing GCP please email [redacted] or call or text [redacted].

## What We're Looking For

- Code quality and structure
- Correctness and completeness
- Testing approach
- Deployment automation
- Documentation clarity
- Security and cost awareness
- Communication of your approach

## Task

We want you to create a simple website that contains a form with the following fields:

- First Name (text)
- Last Name (text)
- Email Address (email)
- What is your favourite colour? (select list with red, green blue)

All fields are required. Form validation should happen on both the frontend and backend.

You don't need to use a framework like react, nor does it need to look pretty.

- Once submitted the form fields should be added to a database.
- The user should be notified with a message advising them that the submission was successful or not.
- The form should run on flask with Google Cloud Run and the database on Cloud SQL.
- You should create units test e.g. you may want to use mock to simulate database submissions.
- You should create a make command that creates the database and schema.
- You should create a make command that deploys the flask code to a cloud run app.
- Any credentials should be added to an .env file.

## Deliverables

You should deploy your code and database to GCP and you should have submitted a number of tests submissions to the database.

You should provide a zip via email to [redacted] containing:

- Your source code.
- .env file (with dummy secrets only)
- A README.md file containing:
  - Instructions on how to deploy the database and flask app to GCP.
  - A link to the form on CloudRun.
  - Instructions on how to run your tests
  - An explanation of how the code is structured, where files are etc.
