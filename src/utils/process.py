import time
import json
from utils.watch import logger
from data.insert import insert_scan, insert_tables_rules


def process_message(message):
    # Deserialize the message
    data = json.loads(message)

    # Process the scan data and get the scan_id
    scan_id = process_tables_scans(data['tables_scans'])

    # Insert data into the axe.rules table
    tables_rules = data.get('tables_rules', [])
    insert_tables_rules(scan_id, tables_rules)


def process_tables_scans(tables_scans):
    # Extract data from 'tables_scans'
    engine_name = tables_scans['engine_name']
    orientation_angle = tables_scans['orientation_angle']
    orientation_type = tables_scans['orientation_type']
    user_agent = tables_scans['user_agent']
    window_height = tables_scans['window_height']
    window_width = tables_scans['window_width']
    scanned_at = tables_scans['scanned_at']
    url_id = tables_scans['url_id']
    url = tables_scans['url']

    scan_id = insert_scan(
        engine_name, orientation_angle, orientation_type,
        user_agent, window_height, window_width,
        scanned_at, url_id, url
    )
    logger.debug(f'Created Scan ID: {scan_id}')
    return scan_id
