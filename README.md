# django-firebase

Spark Automotive: Smart Cashier System

Project Overview
Spark Automotive is a smart cashier system designed to streamline the payment and service tracking process for automotive repair businesses. This application provides a real-time, touch-enabled interface for cashiers to manage client orders and a live-updating display for customers to view their service and payment status.
This project is built to improve operational efficiency and enhance the customer experience by providing transparency and automation in the service workflow.

Key Features

Real-time Updates: Utilizes WebSockets to provide instant updates on service progress and financial summaries to the client display screen.

Responsive Design: The cashier and client interfaces are designed to be fully responsive, ensuring a clean and professional look on various devices, from desktop monitors to touch-screen terminals.

Secure Payments: A dedicated payment terminal for cashiers simplifies the payment process with a clean, comma-formatted number input for accurate data entry.

Automatic Receipt Generation: Generates clean, printer-friendly receipts that can be printed instantly, providing a professional and organized record for both the business and the customer.

Centralized Data Management: Integrates with a backend database (e.g., Firestore) to centrally manage orders, client details, and service status.

Technologies Used

Backend:

Python: The core language for the application logic.

Django: The web framework for building the application, including the admin interface and routing.

Django Channels: Enables WebSocket functionality for real-time communication.

Gunicorn / Daphne: ASGI server for handling asynchronous requests in a production environment.

Frontend:

HTML5: For structuring the web pages.
CSS3 / Tailwind CSS: For modern, utility-first styling and responsive design.
JavaScript: For dynamic client-side interactions, including real-time updates and input formatting.

Database:

Firestore: A NoSQL cloud database for storing and managing order data.
Deployment:
Render: A cloud platform used for deploying the application with full support for Django, WebSockets, and database services.

Installation and Setup
Prerequisites
Python 3.8+

pip (Python package installer)
Git

Steps

Clone the Repository:

Bash

git clone https://github.com/opiodaniel/django-firebase.git

cd your-repository-name

Create and Activate a Virtual Environment:

Bash

python -m venv venv

source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

Install Dependencies:

Bash

pip install -r requirements.txt

Configure Database:

Set up your Firestore project and download the service account key.

Add your database credentials to settings.py or as environment variables.


python manage.py migrate

Run the Development Server:

Bash

python manage.py runserver
The application will be available at http://127.0.0.1:8000.

Contact
For questions or support, please contact the developer at danielopio540@gmail.com
