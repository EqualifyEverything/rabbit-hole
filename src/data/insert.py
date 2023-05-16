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


def execute_insert(query, params=None, return_id=True, cur=None, expect_result=True):
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
        if expect_result:
            if return_id:
                result = cur.fetchone() or ()  # return an empty tuple if None
            else:
                result = cur.rowcount
                logger.debug(f'🗄️✏️ Rows affected: {result}')
        else:
            result = None
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


def record_error(queue, url_id, error_message):
    query = """
        INSERT INTO results.errors (
            url_id, error_message, queue
        ) VALUES (
            %s, %s, %s
        )
        ON CONFLICT (url_id, error_message, queue) DO UPDATE SET
            updated_at = NOW();
    """
    params = (url_id, error_message, queue)
    execute_insert(query, params, expect_result=False)
    logger.debug(f'Recorded Error from {queue}')


# Insert Uppies Results
def record_uppies(url_id, data):
    query = """
        INSERT INTO results.scan_uppies (
            url_id,
            status_code,
            content_type,
            response_time,
            charset,
            page_last_modified,
            content_length,
            server,
            x_powered_by,
            x_content_type_options,
            x_frame_options,
            x_xss_protection,
            content_security_policy,
            strict_transport_security,
            etag
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """
    # Prepare the data for insert
    page_last_modified = data.get('page_last_modified') or None
    content_length = data.get('content_length')
    if content_length == '':
        content_length = None
    status_code = data.get('status_code')
    if not status_code:
        status_code = 997

    params = (
        url_id,
        status_code,
        data.get('content_type'),
        data.get('response_time'),
        data.get('charset'),
        page_last_modified,
        content_length,
        data.get('server'),
        data.get('x_powered_by'),
        data.get('x_content_type_options'),
        data.get('x_frame_options'),
        data.get('x_xss_protection'),
        data.get('content_security_policy'),
        data.get('strict_transport_security'),
        data.get('etag'),
    )
    execute_insert(query, params, expect_result=False)
    logger.debug(f'Uppies record inserted for URL ID: {url_id}')


