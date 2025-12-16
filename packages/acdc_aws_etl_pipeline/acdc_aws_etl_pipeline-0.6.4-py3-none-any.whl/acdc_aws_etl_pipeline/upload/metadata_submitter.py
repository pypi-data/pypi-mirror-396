import os
# redefine to use local cache in /tmp
os.environ['XDG_CACHE_HOME'] = '/tmp/.cache'

import json
import boto3
from gen3.auth import Gen3Auth
from gen3.index import Gen3Index
from gen3.submission import Gen3Submission
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def create_boto3_session(aws_profile: str = None):
    """
    Create and return a boto3 Session object using an optional AWS profile.

    Args:
        aws_profile (str, optional): The AWS CLI named profile to use for credentials. If None, uses default credentials.

    Returns:
        boto3.Session: The created session instance.
    """
    logger.debug(f"Creating boto3 session with aws_profile={aws_profile}")
    return boto3.Session(profile_name=aws_profile) if aws_profile else boto3.Session()

def is_s3_uri(s3_uri: str) -> bool:
    """
    Check if the provided URI is a valid S3 URI.

    Args:
        s3_uri (str): The string to check.

    Returns:
        bool: True if the string starts with 's3://', False otherwise.
    """
    logger.debug(f"Checking if {s3_uri} is an S3 URI.")
    return s3_uri.startswith("s3://")

def get_filename(file_path: str) -> str:
    """
    Extract the filename from a file path.

    Args:
        file_path (str): The full path to a file.

    Returns:
        str: The filename (with extension).
    """
    filename = file_path.split("/")[-1]
    logger.debug(f"Extracted filename '{filename}' from file_path '{file_path}'.")
    return filename

def get_node_from_file_path(file_path: str) -> str:
    """
    Extract the node name from a file path, assuming file is named as 'node.json'.

    Args:
        file_path (str): The file path.

    Returns:
        str: The base node name before the extension.
    """
    filename = get_filename(file_path)
    node = filename.split(".")[0]
    logger.debug(f"Extracted node '{node}' from filename '{filename}'.")
    return node

def list_metadata_jsons(metadata_dir: str) -> list:
    """
    List all .json files in a given directory.

    Args:
        metadata_dir (str): Directory containing metadata JSON files.

    Returns:
        list: List of absolute paths to all .json files in the directory.

    Raises:
        Exception: If there is an error reading the directory.
    """
    try:
        logger.info(f"Listing .json files in metadata directory: {metadata_dir}")
        files = os.listdir(metadata_dir)
        return [os.path.abspath(os.path.join(metadata_dir, f)) for f in files if f.endswith(".json")]
    except Exception as e:
        logger.error(f"Error listing metadata JSONs in {metadata_dir}: {e}")
        raise

def find_data_import_order_file(metadata_dir: str) -> str:
    """
    Find the DataImportOrder.txt file within a directory.

    Args:
        metadata_dir (str): Directory to search in.

    Returns:
        str: Full path to the DataImportOrder.txt file.

    Raises:
        FileNotFoundError: If no such file is found.
    """
    try:
        logger.info(f"Searching for DataImportOrder.txt in {metadata_dir}")
        files = [os.path.join(metadata_dir, f) for f in os.listdir(metadata_dir)]
        order_files = [f for f in files if "DataImportOrder.txt" in f]
        if not order_files:
            logger.error("No DataImportOrder.txt file found in the given directory.")
            raise FileNotFoundError("No DataImportOrder.txt file found in the given directory.")
        logger.debug(f"Found DataImportOrder.txt file: {order_files[0]}")
        return order_files[0]
    except Exception as e:
        logger.error(f"Error finding DataImportOrder.txt in {metadata_dir}: {e}")
        raise

def list_metadata_jsons_s3(s3_uri: str, session) -> list:
    """
    List all .json files in an S3 "directory" (prefix).

    Args:
        s3_uri (str): S3 URI to the metadata directory (e.g. "s3://my-bucket/path/to/dir").
        session (boto3.Session): An active boto3 Session.

    Returns:
        list: List of S3 URIs for all .json files found under the prefix.
    """
    logger.info(f"Listing .json files in S3 metadata directory: {s3_uri}")
    s3 = session.client('s3')
    bucket = s3_uri.split("/")[2]
    prefix = "/".join(s3_uri.split("/")[3:])
    if prefix and not prefix.endswith("/"):
        prefix += "/"  # Ensure prefix ends with a slash for directories

    objects = s3.list_objects(Bucket=bucket, Prefix=prefix)
    result = [
        f"s3://{bucket}/{obj['Key']}"
        for obj in objects.get('Contents', [])
        if obj['Key'].endswith(".json")
    ]
    logger.debug(f"Found {len(result)} .json files in S3 at {s3_uri}")
    return result

def find_data_import_order_file_s3(s3_uri: str, session) -> str:
    """
    Search for the DataImportOrder.txt file in an S3 directory.

    Args:
        s3_uri (str): S3 URI specifying the directory/prefix to search.
        session (boto3.Session): An active boto3 Session.

    Returns:
        str: Full S3 URI of the found DataImportOrder.txt file.

    Raises:
        FileNotFoundError: If the file does not exist in the specified prefix.
    """
    logger.info(f"Searching for DataImportOrder.txt in S3 metadata directory: {s3_uri}")
    s3 = session.client('s3')
    bucket = s3_uri.split("/")[2]
    prefix = "/".join(s3_uri.split("/")[3:])
    objects = s3.list_objects(Bucket=bucket, Prefix=prefix)
    order_files = [obj['Key'] for obj in objects.get('Contents', []) if obj['Key'].endswith("DataImportOrder.txt")]
    if not order_files:
        logger.error("No DataImportOrder.txt file found in the given S3 directory.")
        raise FileNotFoundError("No DataImportOrder.txt file found in the given directory.")
    logger.debug(f"Found DataImportOrder.txt file in S3: s3://{bucket}/{order_files[0]}")
    return f"s3://{bucket}/{order_files[0]}"

def read_metadata_json(file_path: str) -> dict:
    """
    Read and return a JSON file from the local file system.

    Args:
        file_path (str): Path to the .json file.

    Returns:
        dict or list: Parsed contents of the JSON file.
    """
    logger.info(f"Reading metadata json from local file: {file_path}")
    with open(file_path, "r") as f:
        data = json.load(f)
    logger.debug(f"Read {len(data) if isinstance(data, list) else 'object'} objects from {file_path}")
    return data

def read_metadata_json_s3(s3_uri: str, session) -> dict:
    """
    Read and return JSON data from an S3 file.

    Args:
        s3_uri (str): Full S3 URI to the .json file.
        session (boto3.Session): Boto3 session.

    Returns:
        dict or list: Parsed JSON object from S3 file.
    """
    logger.info(f"Reading metadata json from S3 file: {s3_uri}")
    s3 = session.client('s3')
    obj = s3.get_object(Bucket=s3_uri.split("/")[2], Key="/".join(s3_uri.split("/")[3:]))
    data = json.loads(obj['Body'].read().decode('utf-8'))
    logger.debug(f"Read {len(data) if isinstance(data, list) else 'object'} objects from {s3_uri}")
    return data

def read_data_import_order_txt_s3(s3_uri: str, session) -> list:
    """
    Read a DataImportOrder.txt file from S3 and return node order as a list.

    Args:
        s3_uri (str): S3 URI to the DataImportOrder.txt file.
        session (boto3.Session): Boto3 session.

    Returns:
        list: Node names (order as listed in file).

    Raises:
        ValueError: If the provided S3 URI does not point to DataImportOrder.txt.
    """
    filename = s3_uri.split("/")[-1]
    if 'DataImportOrder.txt' not in filename:
        logger.error(f"File {filename} is not a DataImportOrder.txt file")
        raise ValueError(f"File {filename} is not a DataImportOrder.txt file")
    logger.info(f"Reading DataImportOrder.txt from S3 file: {s3_uri}")
    s3 = session.client('s3')
    obj = s3.get_object(Bucket=s3_uri.split("/")[2], Key="/".join(s3_uri.split("/")[3:]))
    content = obj['Body'].read().decode('utf-8')
    import_order = [line.rstrip() for line in content.splitlines() if line.strip()]
    logger.debug(f"Read import order from S3 file: {import_order}")
    return import_order

def read_data_import_order_txt(file_path: str, exclude_nodes: list) -> list:
    """
    Read DataImportOrder.txt from local file, optionally excluding some nodes.

    Args:
        file_path (str): Path to DataImportOrder.txt.
        exclude_nodes (list): Node names to exclude from result.

    Returns:
        list: Node names, excludes specified nodes, keeps listed order.

    Raises:
        FileNotFoundError: If the file is not found.
    """
    try:
        logger.info(f"Reading DataImportOrder.txt from local file: {file_path}")
        with open(file_path, "r") as f:
            import_order = [line.rstrip() for line in f if line.strip()]
            logger.debug(f"Raw import order from file: {import_order}")
            if exclude_nodes is not None:
                import_order = [node for node in import_order if node not in exclude_nodes]
                logger.debug(f"Import order after excluding nodes {exclude_nodes}: {import_order}")
        logger.debug(f"Final import order from {file_path}: {import_order}")
        return import_order
    except FileNotFoundError:
        logger.error(f"Error: DataImportOrder.txt not found in {file_path}")
        return []

def split_json_objects(json_list, max_size_kb=50, print_results=False) -> list:
    """
    Split a list of JSON-serializable objects into size-limited chunks.

    Each chunk/list, when JSON-serialized, will not exceed max_size_kb kilobytes.

    Args:
        json_list (list): List of JSON serializable objects.
        max_size_kb (int, optional): Max chunk size in KB. Default: 50.
        print_results (bool, optional): If True, info log the size/count per chunk. Default: False.

    Returns:
        list: List of lists. Each sublist size (JSON-serialized) <= max_size_kb.
    """
    logger.info(f"Splitting JSON objects into max {max_size_kb} KB chunks. Total items: {len(json_list)}")
    def get_size_in_kb(obj):
        """
        Get the size in kilobytes of the JSON-serialized object.

        Args:
            obj: JSON-serializable object.

        Returns:
            float: Size of the object in kilobytes.
        """
        import sys
        size_kb = sys.getsizeof(json.dumps(obj)) / 1024
        logger.debug(f"Calculated size: {size_kb:.2f} KB")
        return size_kb

    def split_list(json_list):
        """
        Recursively split the list so each chunk fits within max_size_kb.

        Args:
            json_list (list): List to split.

        Returns:
            list: List of sublists.
        """
        if get_size_in_kb(json_list) <= max_size_kb:
            logger.debug(f"Split length {len(json_list)} is within max size {max_size_kb} KB.")
            return [json_list]
        mid = len(json_list) // 2
        left_list = json_list[:mid]
        right_list = json_list[mid:]
        logger.debug(f"Splitting list at index {mid}: left {len(left_list)}, right {len(right_list)}")
        return split_list(left_list) + split_list(right_list)

    split_lists = split_list(json_list)
    if print_results:
        for i, lst in enumerate(split_lists):
            logger.info(f"List {i+1} size: {get_size_in_kb(lst):.2f} KB, contains {len(lst)} objects")
    logger.debug(f"Total splits: {len(split_lists)}")
    return split_lists

def get_gen3_api_key_aws_secret(secret_name: str, region_name: str, session) -> dict:
    """
    Retrieve a Gen3 API key stored as a secret in AWS Secrets Manager and parse it as a dict.

    Args:
        secret_name (str): Name of the AWS secret.
        region_name (str): AWS region where the secret is located.
        session (boto3.Session): Boto3 session.

    Returns:
        dict: Parsed Gen3 API key.

    Raises:
        Exception: On failure to retrieve or parse the secret.
    """
    logger.info(f"Retrieving Gen3 API key from AWS Secrets Manager: secret_name={secret_name}, region={region_name}")
    client = session.client(service_name='secretsmanager', region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except Exception as e:
        logger.error(f"Error getting secret value from AWS Secrets Manager: {e}")
        raise e

    secret = get_secret_value_response['SecretString']

    try:
        secret = json.loads(secret)
        api_key = secret
        logger.debug(f"Retrieved Gen3 API key from secret {secret_name}")
        return api_key
    except Exception as e:
        logger.error(f"Error parsing Gen3 API key from AWS Secrets Manager: {e}")
        raise e

def create_gen3_submission_class(api_key: dict, api_endpoint: str):
    """
    Create and authenticate a Gen3Submission client using a temporary file for API key.

    Args:
        api_key (dict): The Gen3 API key as Python dict.
        api_endpoint (str): Gen3 endpoint (hostname/base API URL).

    Returns:
        Gen3Submission: An authenticated Gen3Submission object.

    Notes:
        The temporary file storing the API key is deleted after use.
    """
    import tempfile

    logger.info(f"Creating Gen3Submission class for endpoint: {api_endpoint}")
    tmp_api_key_path = None
    submit = None

    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".json", dir="/tmp") as tmp_file:
            json.dump(api_key, tmp_file)
            tmp_api_key_path = tmp_file.name
        auth = Gen3Auth(refresh_file=tmp_api_key_path)
        submit = Gen3Submission(endpoint=api_endpoint, auth_provider=auth)
        return submit
    finally:
        if tmp_api_key_path and os.path.exists(tmp_api_key_path):
            try:
                os.remove(tmp_api_key_path)
                logger.debug(f"Temporary API key file {tmp_api_key_path} deleted.")
            except Exception as e:
                logger.warning(f"Failed to delete temporary API key file {tmp_api_key_path}: {e}")

def write_submission_results(results, output_path, mode='w'):
    with open(output_path, mode) as f:
        json.dump(results, f, indent=4)

def submit_metadata(
    file_list: list,
    api_key: str,
    api_endpoint: str,
    project_id: str,
    data_import_order_path: str,
    boto3_session,
    max_size_kb: int = 50,
    exclude_nodes: list = None,
    max_retries: int = 5,
    write_submission_results_path: str = None
):
    """
    Submit a set of metadata JSON files to a Gen3 data commons endpoint, in order.

    Args:
        file_list (list): List of paths (local or S3 URIs) to metadata .json files, one per node type.
        api_key (str): Gen3 API key (parsed dict or JSON string).
        api_endpoint (str): Gen3 data commons endpoint URL.
        project_id (str): Gen3 project ID to submit data to.
        data_import_order_path (str): Path or S3 URI to DataImportOrder.txt specifying submission order.
        boto3_session (boto3.Session): Existing AWS/boto3 session for S3 & secret usage.
        max_size_kb (int, optional): Maximum size per submission chunk, in KB. Default: 50.
        exclude_nodes (list, optional): List of node names to skip (default: ["project", "program", "acknowledgement", "publication"]).
        max_retries (int, optional): Maximum number of retry attempts per node chunk. Default: 5.

    Returns:
        None

    Raises:
        Exception: On critical submission failure for any chunk.

    Notes:
        Each file is split into size-friendly chunks before submit. Local and S3 files are supported.
    """

    timestamp = datetime.now().strftime("%Y%d%m-%H%M%S")
    log_dir = f"submission_logs/{timestamp}"
    os.makedirs(log_dir, exist_ok=True)

    if exclude_nodes is None:
        exclude_nodes = ["project", "program", "acknowledgement", "publication"]

    logger.info("Starting metadata submission process.")
    logger.info(f"Creating Gen3Submission class for endpoint: {api_endpoint}")

    try:
        submit = create_gen3_submission_class(api_key, api_endpoint)

        if is_s3_uri(data_import_order_path):
            logger.info(f"Reading import order from S3: {data_import_order_path}")
            import_order = read_data_import_order_txt_s3(data_import_order_path, boto3_session)
            logger.debug(f"Import order from S3: {import_order}")
        else:
            logger.info(f"Reading import order from file: {data_import_order_path}")
            import_order = read_data_import_order_txt(data_import_order_path, exclude_nodes)
            logger.debug(f"Import order from file: {import_order}")

        file_map = {get_node_from_file_path(file): file for file in file_list}

        for node in import_order:
            if node in exclude_nodes:
                logger.info(f"Skipping node '{node}' (in exclude list).")
                continue
            file = file_map.get(node)
            if not file:
                logger.info(f"Skipping node '{node}' (not present in file list).")
                continue

            logger.info(f"Processing file '{file}' for node '{node}'.")

            try:
                if is_s3_uri(file):
                    logger.info(f"Reading JSON data for node '{node}' from S3 file: {file}")
                    json_data = read_metadata_json_s3(file, boto3_session)
                else:
                    logger.info(f"Reading JSON data for node '{node}' from local file: {file}")
                    json_data = read_metadata_json(file)
            except Exception as e:
                logger.error(f"Error reading JSON for node '{node}' from {file}: {e}")
                raise Exception(f"Failed to read JSON metadata for node '{node}' from {file}: {e}")

            split_json_list = split_json_objects(json_data, max_size_kb=max_size_kb)
            n_json_data = len(split_json_list)
            logger.info(
                f"--- Starting submission process for node '{node}' ({n_json_data} chunks) ---"
            )

            for index, jsn in enumerate(split_json_list):
                progress_str = f"{index + 1}/{n_json_data}"

                submission_success = False
                last_exception = None
                for attempt in range(max_retries + 1):
                    try:
                        log_msg = (
                            f"[SUBMIT]  | Project: {project_id:<10} | Node: {node:<12} | "
                            f"Split: {progress_str:<5}"
                            if attempt == 0 else
                            f"[RETRY]   | Project: {project_id:<10} | Node: {node:<12} | "
                            f"Split: {progress_str:<5} | Attempt: {attempt}/{max_retries}"
                        )
                        logger.info(log_msg) if attempt == 0 else logger.warning(log_msg)

                        res = submit.submit_record("program1", project_id, jsn)

                        if write_submission_results_path is not None:
                            log_filename = os.path.join(
                                log_dir, f"{project_id}_{node}_split{index + 1}_of_{n_json_data}.json"
                            )
                            abs_log_filename = os.path.abspath(log_filename)
                            with open(abs_log_filename, "a") as f:
                                json.dump(res, f)
                                f.write("\n")
                            logger.info(
                                f"Wrote submission response to log file: {abs_log_filename}"
                            )

                        logger.info(
                            f"\033[92m[SUCCESS]\033[0m | Project: {project_id:<10} | "
                            f"Node: {node:<12} | Split: {progress_str:<5}"
                        )
                        submission_success = True
                        break  # Success

                    except Exception as e:
                        last_exception = e
                        logger.error(
                            f"Error submitting chunk {progress_str} for node '{node}': {e}"
                        )
                        if attempt < max_retries:
                            import time
                            time.sleep(0.2)
                        else:
                            logger.critical(
                                f"\033[91m[FAILED]\033[0m  | Project: {project_id:<10} | "
                                f"Node: {node:<12} | Split: {progress_str:<5} | Error: {e}"
                            )

                if not submission_success:
                    # After retries, still failed
                    raise Exception(
                        f"Failed to submit chunk {progress_str} for node '{node}' after {max_retries + 1} attempts. "
                        f"Last error: {last_exception}"
                    )

            logger.info(f"Finished submitting node '{node}'.")

        logger.info("--- Submission process complete ---")

    except Exception as exc:
        logger.exception(f"Critical error during submission process: {exc}")
        raise
