website_monitor/
│── 	                         # Application code
│   ├── flask_monitor.py         # Flask web interface
│   ├── improve_monitor.py       # Runs monitoring on demand
│   ├── monitor_scheduler.py     # Runs periodic monitoring
│── templates/                   # HTML Templates for Flask
│   ├── index.html               # Main UI
│   ├── add_website.html         # Add website form
│   ├── metrics.html             # Metrics graphs
│── requirements.txt             # Required Python packages
│── README.txt                    # Instructions for users




TO RUN PROGRAM need to be in a python virtual environment 
source ~/monitor_env/bin/activate 
python improved_monitor.py
python flask_monitor_app.py
python scheduler_monitor.py


DATABASE:
Login to database
mysql -u monitor_user -p -D website_monitor
Pass: your_password

#Useful commands
SHOW TABLES;
DESCRIBE website_metrics;
DESCRIBE monitored_websites;
SELECT * FROM monitored_websites;
Delete data from the table: TRUNCATE TABLE website_metrics;
Where database files are stored: sudo ls /var/lib/mysql/website_monitor/

DATABASE STRUCTURE:
Run db_setup.py


