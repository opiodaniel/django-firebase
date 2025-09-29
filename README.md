💳 Flashtech Cashier Payment Terminal
This project is a modern, web-based payment terminal designed for the Flashtech automotive workshop. It allows cashiers to efficiently process payments, calculate change, and print receipts for customer orders stored in a Google Firestore database.

Tech Stack
Category	Technology	Purpose
Backend	Django	Python web framework handling routing, business logic, and server-side rendering (using Django templates).
Database	Google Firestore (NoSQL)	Cloud-hosted database for storing and managing order and customer data.
Frontend	HTML5/CSS3	Core structure and basic styling.
Styling	Tailwind CSS	Utility-first CSS framework for rapid and responsive UI development.
Interactivity	AJAX / jQuery / Vanilla JS	Handling real-time payment processing, modal pop-ups, and form submission without full page reloads.
Real-time	Django Channels / WebSockets	Used for the "Client Screen" feature to display transaction updates in real-time.

Project Setup Guide
Follow these steps to get the project running on your local machine.

Prerequisites
You need Python 3.8+ installed on your system.

Clone the Repository
git clone https://github.com/opiodaniel/django-firebase.git
cd django-firebase/web

Set up the Virtual Environment
It's strongly recommended to use a virtual environment to manage dependencies.

python -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

Install Dependencies
Install all required Python packages (including Django, Firebase Admin SDK, and Google Cloud Firestore).

pip install django google-cloud-firestore firebase-admin

Firebase/Firestore Setup
The project relies on a connection to your Google Firestore database.

Create a Firebase Project: If you haven't already, create a new project in the Firebase Console.

Generate Service Account Key:

In the Firebase Console, navigate to Project Settings (⚙️) -> Service accounts.

Click Generate new private key and download the JSON file.

Configure Environment:

Place the downloaded JSON key file (e.g., serviceAccountKey.json) in a secure, accessible directory within your project.

In your Django settings file (settings.py), set the path to this key, or ensure your code initializes the Firebase Admin SDK using the path:

import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK (replace 'path/to/your/key.json')
cred = credentials.Certificate('path/to/your/key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

Database Structure: Ensure you have a collection named flashtech-order with sample data, including a created_at timestamp field for sorting.

Run the Server
Apply Migrations (Standard Django setup):

python manage.py migrate
python manage.py runserver

The application will now be running at http://127.0.0.1:8000/. You can access your order list and payment terminal views from there.