# SRM Welkin ATL Inventory Management System

A web-based inventory management system for SRM Welkin ATL, designed to track and manage equipment and student assignments.

## Features

- Add and manage students
- Add and manage inventory items 
- Assign items to students
- Track assignments and returns
- Search functionality for items, students, and assignments

## Deployment Instructions

### Local Deployment

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```
4. Access the website at `http://127.0.0.1:5000`

### Deployment on Render

1. Create an account on [Render](https://render.com/)

2. From your Render dashboard, click "New" and select "Web Service"

3. Connect your GitHub repository or use the manual deploy option

4. Configure the web service:
   - **Name**: Choose a name for your service (e.g., srm-welkin-atl-inventory)
   - **Environment**: Python
   - **Region**: Choose a region close to your users
   - **Branch**: main (or your default branch)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:application`

5. Set environment variables:
   - Add `FLASK_ENV` = `production`

6. Click "Create Web Service"

7. Render will automatically build and deploy your application
   - The first deployment might take a few minutes
   - Once complete, Render will provide you with a URL to access your website

8. Your application is now deployed and accessible online!

### Deployment on PythonAnywhere

1. Create an account on [PythonAnywhere](https://www.pythonanywhere.com/)
2. Upload all your files to PythonAnywhere using the "Files" tab
3. Create a new web app:
   - Choose "Web" tab > "Add a new web app"
   - Select "Flask" as the framework
   - Choose Python 3.8 or newer
   - Set your app's working directory to where you uploaded the files
   - Set the WSGI file path to point to your application

4. Configure the WSGI file:
   ```python
   import sys
   path = '/home/yourusername/yourprojectpath'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app as application
   ```

5. Install the required packages using the "Consoles" tab:
   ```
   pip install --user -r requirements.txt
   ```

6. Reload the web app from the "Web" tab

## License

&copy; 2023 SRM Welkin ATL - Inventory Management System | Developed by Areeb 