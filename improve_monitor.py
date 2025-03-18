import subprocess
import mysql.connector
from datetime import datetime

# Hardcoded websites that should always be monitored
HARDCODED_WEBSITES = [
    "https://delfi.lt",
    "https://google.com"
]

def run_curl_command(url):
    command = [
        'curl',
        '-w', "time_namelookup:%{time_namelookup},time_connect:%{time_connect},time_appconnect:%{time_appconnect},time_pretransfer:%{time_pretransfer},time_redirect:%{time_redirect},time_starttransfer:%{time_starttransfer},time_total:%{time_total},speed_download:%{speed_download},speed_upload:%{speed_upload},size_download:%{size_download}",
        '-s',
        '-o', '/dev/null',  # Discard the body output
        url
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        print(f"Timeout expired for {url}")
        return "time_namelookup:0,time_connect:0,time_appconnect:0,time_pretransfer:0,time_redirect:0,time_starttransfer:0,time_total:0,speed_download:0,speed_upload:0,size_download:0"
    except Exception as e:
        print(f"Error fetching metrics for {url}: {e}")
        return "time_namelookup:0,time_connect:0,time_appconnect:0,time_pretransfer:0,time_redirect:0,time_starttransfer:0,time_total:0,speed_download:0,speed_upload:0,size_download:0"

def store_data(db_config, url, metrics):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS website_metrics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(255) UNIQUE,
            time_namelookup FLOAT,
            time_connect FLOAT,
            time_appconnect FLOAT,
            time_pretransfer FLOAT,
            time_redirect FLOAT,
            time_starttransfer FLOAT,
            time_total FLOAT,
            speed_download FLOAT,
            speed_upload FLOAT,
            size_download FLOAT,
            timestamp DATETIME
        )
    """)

    # Safely parse metrics
    data = {}
    for item in metrics.split(","):
        if ":" in item:
            k, v = item.split(":", 1)
            try:
                data[k] = float(v)
            except ValueError:
                data[k] = 0.0  # Default to 0 if conversion fails

    data['url'] = url
    data['timestamp'] = datetime.now()

    # Insert or update the record if it already exists
    cursor.execute("""
        INSERT INTO website_metrics (
            url, time_namelookup, time_connect, time_appconnect, time_pretransfer, 
            time_redirect, time_starttransfer, time_total, speed_download, speed_upload, 
            size_download, timestamp
        ) VALUES (%(url)s, %(time_namelookup)s, %(time_connect)s, %(time_appconnect)s, %(time_pretransfer)s,
                  %(time_redirect)s, %(time_starttransfer)s, %(time_total)s, %(speed_download)s, %(speed_upload)s,
                  %(size_download)s, %(timestamp)s)
        ON DUPLICATE KEY UPDATE 
            time_namelookup = VALUES(time_namelookup),
            time_connect = VALUES(time_connect),
            time_appconnect = VALUES(time_appconnect),
            time_pretransfer = VALUES(time_pretransfer),
            time_redirect = VALUES(time_redirect),
            time_starttransfer = VALUES(time_starttransfer),
            time_total = VALUES(time_total),
            speed_download = VALUES(speed_download),
            speed_upload = VALUES(speed_upload),
            size_download = VALUES(size_download),
            timestamp = VALUES(timestamp)
    """, data)

    connection.commit()
    cursor.close()
    connection.close()

def fetch_websites(db_config):
    """ Fetch websites but ensure only HARDCODED ones + new ones are included. """
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitored_websites (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(255) UNIQUE,
            added_on DATETIME
        )
    """)

    cursor.execute("SELECT url FROM monitored_websites")
    db_websites = [row[0] for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    # Ensure only HARDCODED websites + newly added ones appear
    return list(set(HARDCODED_WEBSITES + db_websites))

if __name__ == '__main__':
    # Database configuration
    db_config = {
        'user': 'monitor_user',
        'password': 'your_password',
        'host': 'localhost',
        'database': 'website_monitor'
    }

    # Fetch only necessary websites
    websites = fetch_websites(db_config)

    if not websites:
        print("No websites found in the database. Please add websites to monitor.")
    else:
        for site in websites:
            metrics = run_curl_command(site)
            print(f"Metrics for {site}: {metrics}")
            store_data(db_config, site, metrics)

        print("Monitoring completed.")

