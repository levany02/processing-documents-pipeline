import os
from google.cloud import storage
from docx2md import convert_docx

# Initialize the storage client
storage_client = storage.Client()

def extract_docx_to_md(event, context):
    """Triggered by a change to a Cloud Storage bucket."""
    
    # 1. Get file metadata from the event
    bucket_name = event['bucket']
    file_name = event['name']
    
    # Only process .docx files to avoid infinite loops
    if not file_name.lower().endswith('.docx'):
        print(f"Skipping non-docx file: {file_name}")
        return

    # 2. Setup local temporary paths
    # Cloud Functions allow writing only to the /tmp directory
    local_input_path = f"/tmp/{os.path.basename(file_name)}"
    extract_dir = "/tmp/extracted_assets"
    
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    # 3. Download the file from GCS to /tmp
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.download_to_filename(local_input_path)
    print(f"Downloaded {file_name} to {local_input_path}")

    # 4. Extract content using docx2md
    # convert_docx returns the markdown string and saves images to extract_dir
    try:
        output_md_content = convert_docx(local_input_path, extract_dir)
        print(output_md_content)
        
        # 5. Define output paths
        # We'll save the output in an 'extracted/' folder in the same bucket
        # output_folder_prefix = f"extracted/{os.path.splitext(file_name)[0]}"
        # # Upload the Markdown file
        # md_blob_name = f"{output_folder_prefix}/index.md"
        # output_blob = bucket.blob(md_blob_name)
        # output_blob.upload_from_string(output_md_content, content_type='text/markdown')
        # print(f"Uploaded markdown to {md_blob_name}")

        # # Upload images/assets extracted by docx2md
        # for root, dirs, files in os.walk(extract_dir):
        #     for file in files:
        #         local_file_path = os.path.join(root, file)
        #         # Maintain folder structure for assets
        #         gcs_file_path = f"{output_folder_prefix}/{file}"
        #         asset_blob = bucket.blob(gcs_file_path)
        #         asset_blob.upload_from_filename(local_file_path)
        #         print(f"Uploaded asset: {gcs_file_path}")

    except Exception as e:
        print(f"Error processing document: {e}")
    finally:
        # Cleanup /tmp to save memory
        if os.path.exists(local_input_path):
            os.remove(local_input_path)