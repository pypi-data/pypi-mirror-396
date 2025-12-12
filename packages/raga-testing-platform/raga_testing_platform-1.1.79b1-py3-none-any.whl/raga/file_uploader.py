import csv
import json
import os
import threading
import time
import requests
import logging
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from urllib.parse import urlparse, urlunparse


class FileUploader:
    def __init__(self, dataset_id, test_session, batch_workers=None, upload_workers=None, csv_path=None):
        self.dataset_id = dataset_id
        self.test_session = test_session
        self.batch_executor = ThreadPoolExecutor(max_workers=batch_workers)
        self.upload_executor = ThreadPoolExecutor(max_workers=upload_workers)
        self.logger = self._setup_logger()
        # CSV file path for storing image names and URIs
        self.csv_path = csv_path or "file_uris.csv"
        self.csv_lock = threading.Lock()  # Thread lock for CSV file operations

    def _setup_logger(self):
        logger = logging.getLogger("FileUploader")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _initialize_csv(self):
        """Initialize CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['ImageId', 'ImageUri'])
            self.logger.info(f"Created CSV file at {self.csv_path}")

    def _save_to_csv(self, image_data):
        with self.csv_lock:
            try:
                # Append mode to add to existing file
                with open(self.csv_path, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    for img_name, img_uri in image_data:
                        writer.writerow([img_name, img_uri])
                self.logger.info(f"Saved {len(image_data)} entries to CSV")
            except Exception as e:
                self.logger.error(f"Failed to save to CSV: {e}")

    def _extract_base_uri_from_presigned(self, presigned_url):
        try:
            parsed_url = urlparse(presigned_url)
            from urllib.parse import unquote
            decoded_path = unquote(parsed_url.path)

            # Remove query parameters and use decoded path
            clean_url = urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                decoded_path,
                '', '', ''  # No params, query, or fragment
            ))
            return clean_url
        except Exception as e:
            self.logger.warning(f"Failed to extract base URI from presigned URL: {e}")
            return None

    def process_batches(self, batch_size, local_directory):

        file_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.tiff', '.pdf']
        # Initialize CSV file first to ensure headers are present
        self._initialize_csv()

        upload_state =  {"uploaded": []}
        previously_uploaded = set(upload_state["uploaded"])

        # Get list of image files
        asset_files = []
        skipped_files = []

        for root, _, files in os.walk(local_directory):
            for file in files:
                file_extension = os.path.splitext(file)[1].lower()
                if file_extension in file_extensions:
                    local_path = os.path.join(root, file)
                    file_name = os.path.basename(local_path)
                    # Skip already uploaded files
                    if file_name  in previously_uploaded:
                        skipped_files.append(file_name)
                    else:
                        asset_files.append((local_path, file_name))

        total_files = len(asset_files)
        if total_files == 0:
            self.logger.info("No files to upload.")
            return 0, 0  # Return zeros if no files to upload
        self.logger.info(f"Found {total_files} files to upload.")

        if len(skipped_files) > 0:
             self.logger.info(f"Skipping {len(skipped_files)} previously uploaded files.")

        # Process in batches
        successful = 0
        failed = 0
        failed_uploads = []
        all_results = []

        # Create batch futures
        batch_futures = []
        total_batches = (total_files + batch_size - 1) // batch_size
        for i in range(0, total_files, batch_size):
            batch = asset_files[i:i + batch_size]
            batch_num = i // batch_size + 1
            self.logger.info(f"\nSubmitting batch {batch_num}/{total_batches} ({len(batch)} files)")

            future = self.batch_executor.submit(
                self.process_file_upload,
                batch,
                batch_num,
                total_batches
            )
            batch_futures.append((future, batch_num, batch))

        # Process batch results as they complete
        with tqdm(total=len(batch_futures), desc="Processing batches") as batch_progress:
            for future, batch_num, batch in batch_futures:
                try:
                    result = future.result()
                    success, message, processed_batch, error_details, uris = result
                    all_results.append((success, message, processed_batch))
                    if success:
                        # Only count as successful if the entire batch succeeded
                        successful += len(processed_batch)
                        # Add to upload state
                        for item in processed_batch:
                            upload_state["uploaded"].append(item[1])  # Add file_name to uploaded list

                        # Save successful uploads to CSV
                        if uris:
                            self._save_to_csv(uris)
                    else:
                        # Count all files in batch as failed if batch processing failed
                        failed += len(processed_batch)
                        failed_uploads.append(f"Batch {batch_num}: {message}")
                        if error_details:
                            for file_name, error in error_details.items():
                                failed_uploads.append(f"  - {file_name}: {error}")
                    batch_progress.update(1)
                    self.logger.info(f"Batch {batch_num} completed: {message}")
                except Exception as e:
                    all_results.append((False, str(e), batch))
                    failed += len(batch)
                    failed_uploads.append(f"Batch {batch_num}: {str(e)}")
                    batch_progress.update(1)
                    print(f"Batch {batch_num} failed: {str(e)}")\

                self.logger.info(f"Progress: {successful} successful, {failed} failed")
                time.sleep(0.5)  # Small pause between batch completions

        # Display summary after all batches complete
        self.logger.info("\nUpload Summary:")
        self.logger.info(f"Total files processed: {total_files}")
        self.logger.info(f"Skipped (previously uploaded): {len(skipped_files)}")
        self.logger.info(f"Successfully uploaded: {successful}")
        self.logger.info(f"Failed uploads: {failed}")
        self.logger.info(f"File URIs saved to: {self.csv_path}")

        if failed > 0:
            self.logger.info("\nFailed batches:")
            for failure in failed_uploads:
                print(f"- {failure}")

        return successful, failed, len(skipped_files), self.csv_path

    def process_file_upload(self, batch, batch_num, total_batches):
        try:
            files = [x[1] for x in batch]
            self.logger.info(f"Requesting pre-signed upload URLs for batch {batch_num}...")
            signed_upload_paths, s3_file_path = self.get_pre_signed_s3_url(files)
            self.logger.info(f"Pre-signed URLs generated successfully | Batch: {batch_num}/{total_batches} | Files: {len(files)} ")
            success, message, error_details = self.upload_batch_with_presigned_urls(batch, signed_upload_paths, s3_file_path )
            # Prepare image URIs for successful uploads by extracting from presigned URLs
            if success:
                file_name_and_uris = []
                for file_name, presigned_url in zip(files, signed_upload_paths):
                    base_uri = self._extract_base_uri_from_presigned(presigned_url)
                    file_name_and_uris.append((file_name, base_uri))
            return success, message, batch, error_details, file_name_and_uris
        except Exception as e:
            self.logger.error(f"Error in batch processing: {str(e)}")
            return False, str(e), batch, {}, [] #Return empty dict and [] for error_details, uris if exception

    def upload_batch_with_presigned_urls(self, batch, signed_upload_paths, s3_file_path):
        upload_results = []
        error_details = {}
        total_files = len(signed_upload_paths)
        local_paths = [item[0] for item in batch]
        file_names = [item[1] for item in batch]

        try:
            file_futures = []
            for local_path, file_name, signed_url, remote_path in zip(local_paths, file_names, signed_upload_paths, s3_file_path):
                future = self.upload_executor.submit(
                    self.upload_local_file,
                    signed_url,
                    local_path
                )
                file_futures.append((future, file_name))

            with tqdm(total=len(file_futures), desc="Uploading files") as progress_bar:
                for future, file_name in file_futures:
                    progress_bar.update(1)
                    try:
                        success, message = future.result()
                        upload_results.append((success, message))
                        if not success:
                            error_details[file_name] = message
                    except Exception as e:
                        error_msg = f"Upload error: {str(e)}"
                        upload_results.append((False, error_msg))
                        error_details[file_name] = error_msg

            # Check if all uploads were successful
            all_success = all(result[0] for result in upload_results)
            if all_success:
                return True, "All files uploaded successfully", None
            else:
                failed_count = sum(1 for result in upload_results if not result[0])
                return False, f"Failed to upload {failed_count} out of {total_files} files", error_details

        except Exception as e:
            error_msg = f"Batch upload error: {str(e)}"
            return False, error_msg, {"batch_error": error_msg}

    def get_pre_signed_s3_url(self, file_names):
        try:
            res_data = self.test_session.http_client.post(
                f"api/dataset/upload/preSignedUrls",
                {"datasetId": self.dataset_id, "fileNames": file_names, "contentType": "application/octet-stream"},
                {"Authorization": f'Bearer {self.test_session.token}'},
            )
            if res_data.get("data") and "urls" in res_data["data"] and "filePaths" in res_data["data"]:
                # self.logger.info("Pre-signed URLs generated")
                return res_data["data"]["urls"], res_data["data"]["filePaths"]
            else:
                error_message = "Failed to get pre-signed URL. Required keys not found in the response."
                self.logger.error(error_message)
                raise ValueError(error_message)
        except Exception as e:
            self.logger.error(f"An error occurred while getting pre-signed URL: {str(e)}")
            raise

    def shutdown(self):
        """Properly shut down both executors"""
        self.logger.info("Shutting down executors...")

        self.logger.info("Shutting down batch executor...")
        self.batch_executor.shutdown(wait=True)

        self.logger.info("Shutting down upload executor...")
        self.upload_executor.shutdown(wait=True)

        self.logger.info("All executors shut down successfully")

    def upload_local_file(self, pre_signed_url, file_path):
        if not pre_signed_url:
            return False, "Pre-signed URL is required"
        if not file_path:
            return False, "File path is required"
        if not os.path.isfile(file_path):
            return False, f"Invalid file path: {file_path}"

        try:
            with open(file_path, "rb") as file:
                headers = {"Content-Type": "application/octet-stream"}
                if "blob.core.windows.net" in pre_signed_url:  # Azure
                    headers["x-ms-blob-type"] = "BlockBlob"
                response = requests.put(pre_signed_url, data=file, headers=headers)
                response.raise_for_status()  # Raise an exception for HTTP errors
                if response.status_code == 200 or response.status_code == 201:
                    return True, "Success"
                else:
                    error_msg = f"HTTP Error: {response.status_code}"
                    try:
                        # Try to get more detailed error message from response
                        error_content = response.text[:200]  # Limit to first 200 chars
                        error_msg = f"{error_msg} - {error_content}"
                    except:
                        pass
                    return False, error_msg
        except requests.RequestException as e:
            return False, f"Request error: {str(e)}"
        except Exception as e:
            return False, f"Error uploading file: {str(e)}"
