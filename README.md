# EduPulse

## Introduction

Welcome to **EduPulse**, a Learning Management System (LMS) that is being developed for Whitecliffe College School of Information Technology. This repository contains the source code for the **EduPulse** web application project. It has been created as part of the Project assessment for IT6041 Software Project course that is part of the Diploma of Software Development programme at Whitecliffe's School of Information Technology.

Please follow the instructions below to get started with setting up the project on your local machine and collaborating with the team.

---

## Table of Contents

- [EduPulse](#edupulse)
  - [Introduction](#introduction)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
    - [Cloning the Repository](#cloning-the-repository)
    - [Setting Up the Development Environment](#setting-up-the-development-environment)
    - [Running the Project](#running-the-project)
      - [Running the Watcher Server](#running-the-watcher-server)
      - [Running the Django Development Server](#running-the-django-development-server)

---

## Installation

### Cloning the Repository

To get started, you'll first need to clone the **EduPulse** repository to your local machine.

1. Open your terminal or command prompt.
2. Navigate to the directory where you want to clone the repository.
3. Run the following command:

```
git clone https://github.com/Whitecliffe-Devs/edupulse.git
```

4. Once the repository has been cloned, navigate to the project's outer **edupulse/** root directory:

```
cd edupulse
```

### Setting Up the Development Environment

Before running the project, please ensure you have the following prerequisites installed on your machine by following these instructions to set up the development environment:

- asgiref==3.7.2
- Django==4.2.6
- django-browser-reload==1.12.0
- sqlparse==0.4.4

1. Create a Python virtual environment. Here we've used ".venv" as the name of the virtual environment:

```
python -m venv .venv
```

2. Activate the virtual environment:

For MacOS/Linux:

```
source .venv/bin/activate
```

For Windows:

```
.venv\Scripts\activate
```

3. Install the project's prerequisites:

```
pip install -r requirements.txt
```

4. This project utilises Tailwind CSS for styling. Install the project's dependencies:

```
npm install
```

5. Apply the project's database migrations:

```
python manage.py migrate
```

### Running the Project

To run the **EduPulse** project during development, you will need to run a "watcher" server and the Django development server in two separate terminals.

#### Running the Watcher Server

1. Open a terminal in VS Code.
2. Ensure you are in the project's outer **edupulse/** root directory.
3. Run the watcher server with the following command:

```
npm run dev
```

#### Running the Django Development Server

1. Open a new terminal in VS Code.
2. Ensure you are in the project's outer **edupulse/** root directory.
3. Run the Django development server with the following command:

```
python manage.py runserver
```

Once successfully started, you can open your browser and navigate to http://localhost:8000 to view the project. Any changes you make to the project's source code should be automatically reflected in the browser.

---
