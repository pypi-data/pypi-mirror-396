import requests
import os


def save_cellx(url, local_filename, folder):

    hiden_folder_name = f"{os.path.expanduser('~')}/{folder}"
    output_path = f"{hiden_folder_name}/{local_filename}"
    if not os.path.isfile(output_path):
        os.makedirs(hiden_folder_name, exist_ok=True)
        print(f"Starting download CellX model from: {url}")
        try:
            # Send a GET request to the URL. We use stream=True to handle large files.
            with requests.get(url, stream=True) as r:
                # Raise an exception for bad status codes (4xx or 5xx)
                r.raise_for_status() 
                
                # Open the local file in binary write mode
                with open(output_path, 'wb') as f:
                    # Iterate over the response content in chunks
                    for chunk in r.iter_content(chunk_size=8192):
                        # Write the chunk to the local file
                        f.write(chunk)

            print(f"Download completed successfully. File saved as: {output_path}")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the download: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

save_cellx("https://zenodo.org/records/17849583/files/CellX.pth", "CellX.pth", ".Cellx")