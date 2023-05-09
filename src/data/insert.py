import time
import json
import traceback
from data.access import connection
from utils.watch import logger
from psycopg2.pool import SimpleConnectionPool

# Set use_pooling to True to enable connection pooling
use_pooling = True

# Connection pool
pool = None

if use_pooling:
    conn_params = connection().get_connection_params()
    pool = SimpleConnectionPool(
        minconn=1,
        maxconn=50,
        **conn_params
    )


def connection_pooling():
    return pool.getconn()


def release_pooling(conn):
    pool.putconn(conn)

# Normal Insert


def execute_insert(query, params=None, return_id=True, cur=None):
    # Connect to the database
    if use_pooling:
        conn = connection_pooling()
    else:
        conn = connection()
        conn.open()
        logger.debug("🗄️✏️ Database connection opened")

    # Create a cursor
    if not cur:
        cur = conn.cursor()
        close_cursor = True
    else:
        close_cursor = False

    try:
        # Execute the query
        cur.execute(query, params)
        conn.commit()
        logger.debug("🗄️✏️🟢 Query executed and committed")

        # Fetch the results if requested
        result = None
        if return_id:
            result = cur.fetchone() or ()  # return an empty tuple if None
        else:
            result = cur.rowcount
            logger.debug(f'🗄️✏️ Rows affected: {result}')
    except Exception as e:
        logger.error(f"🗄️✏️ Error executing insert query: {e}\n{traceback.format_exc()}")
        logger.error(f"🗄️✏️ Failed query: {query}")
        logger.error(f"🗄️✏️ Failed query parameters: {params}")
        time.sleep(5)
        result = None

    # Close the cursor and connection
    if close_cursor:
        cur.close()
    if use_pooling:
        release_pooling(conn)
    else:
        conn.close()
        logger.debug("🗄️✏️ Cursor and connection closed")

    return result


# # # # # # # # # #

# Bulk Inserts

def execute_bulk_insert(query, params_list):
    # Connect to the database
    if use_pooling:
        conn = connection_pooling()
    else:
        conn = connection()
        conn.open()

    # Create a cursor
    cur = conn.cursor()
    rows_affected = 0
    try:
        # Execute the query
        with conn:
            cur.executemany(query, params_list)
            rows_affected = cur.rowcount  # Get the number of rows affected
            logger.debug("🗄️✏️🟢 Query executed and committed")
    except Exception as e:
        logger.error(f"🗄️✏️ Error executing bulk insert query: {e}\n{traceback.format_exc()}")
        logger.error(f"🗄️✏️ Failed query: {query}")
        logger.error(f"🗄️✏️ Failed query parameters: {params_list}")

    # Close the cursor and connection
    cur.close()
    if use_pooling:
        release_pooling(conn)
    else:
        conn.close()

    return rows_affected


# # # # # # # # # #
# Queries


def insert_scan(
    engine_name, orientation_angle, orientation_type, user_agent,
    window_height, window_width, scanned_at, url_id, url
):
    query = """
        INSERT INTO axe.scan_data (
            engine_name, orientation_angle, orientation_type,
            user_agent, window_height, window_width,
            scanned_at, url_id, url
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id;
    """

    params = (
        engine_name, orientation_angle, orientation_type,
        user_agent, window_height, window_width,
        scanned_at, url_id, url
    )

    scan_id = execute_insert(query, params)
    if not scan_id:
        raise ValueError("Error inserting scan data")

    return scan_id[0]


def insert_tables_rules(scan_id, tables_rules):
    query = """
        INSERT INTO axe.rules (
            scan_id, rule_type, axe_id, impact, tags, nodes
        ) VALUES (%s, %s, %s, %s, %s, %s);
    """

    # Prepare the data for bulk insert
    params_list = []
    for rule in tables_rules:
        # Convert the tags string to a JSON array
        tags_json = json.dumps(rule['tags'].split(','))

        params = (
            scan_id,
            rule['rule_type'],
            rule['axe_id'],
            rule['impact'],
            tags_json,
            rule.get('nodes', None)
        )
        params_list.append(params)

    # Perform the bulk insert
    rows_affected = execute_bulk_insert(query, params_list)
    logger.debug(f'Rules Inserted: {rows_affected}')
    return rows_affected

def create_crawl(
        url_id, urls_found
    ):
        query = """
            INSERT INTO results.crawl (
                url_id, urls_found
            ) VALUES (
                %s, %s
            ) RETURNING id;
        """

        params = (
            url_id, urls_found
        )

        crawl_id = execute_insert(query, params)
        if not crawl_id:
            raise ValueError("Error creating new crawl")

        return crawl_id[0]


def record_urls(scan_id, url_id, urls):
    query = """
        INSERT INTO targets.urls (
            url, crawled_at, source_url_id,
            recent_crawl_id, discovery_crawl_id
        ) VALUES (
            %s, NOW(), %s, %s, %s
        )
        ON CONFLICT (url) DO UPDATE SET
            crawled_at = NOW(),
            recent_crawl_id = EXCLUDED.recent_crawl_id
        RETURNING id;
    """

    # Prepare the data for bulk insert
    params_list = [(url, url_id, scan_id, scan_id) for url in urls]

    # Perform the bulk insert
    url_ids = execute_bulk_insert(query, params_list)
    logger.debug(f'URLs Inserted/Updated: {url_ids}')
    return url_ids
