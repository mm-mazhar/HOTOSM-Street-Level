import csv
import os
import sys
import time
import typing
import webbrowser
from typing import Any

# Add project root directory to Python path
sys.path.append(
    os.path.abspath(path=os.path.join(os.path.dirname(p=__file__), "../../"))
)

import requests
from dotenv import load_dotenv

from configs import cfgs

# Load environment variables
load_dotenv()

# YOUR API KEYS/SECRETS (KEEP THESE SAFE!)
CLIENT_ID: str | None = os.environ.get("CLIENT_ID")
CLIENT_SECRET: str | None = os.environ.get("CLIENT_SECRET")
AUTHORIZATION_URL: str | None = os.environ.get("AUTHORIZATION_URL")
REDIRECT_URI: str | None = os.environ.get("REDIRECT_URI")

OUTPUT_DIRECTORY: str = os.path.join(
    cfgs["BASE_DATA_DIRECTORY"], "images", cfgs["COUNTRY"]["REGION"]["NAME"]
)
CSV_DIRECTORY: str = os.path.join(cfgs["BASE_DATA_DIRECTORY"], "csv/")

# Initially, we don't have the token
ACCESS_TOKEN: typing.Optional[str] = None

# print(cfgs["COUNTRY"]["REGION"]["NAME"])


def get_authorization_code() -> str:
    """Opens the authorization URL in the user's browser and prompts them to authorize."""
    authorization_url: str = (
        f"{AUTHORIZATION_URL}"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=read write upload"  # Adjust the scope as needed
    )
    print(f"Opening authorization URL: {authorization_url}")
    webbrowser.open(url=authorization_url)
    # Prompt the user to enter the authorization code from the redirected URL
    authorization_code: str = input(
        "Please enter the authorization code from the Mapillary connect page: "
    )
    return authorization_code


def get_access_token(authorization_code) -> Any | None:
    """Exchanges an authorization code for an access token."""
    token_url = "https://graph.mapillary.com/token"
    payload: dict[str, Any] = {
        "grant_type": "AUTHORIZATION_CODE",
        "code": authorization_code,
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
    }
    headers: dict[str, str] = {
        "Authorization": f"OAuth {CLIENT_SECRET}",
        "Content-Type": "application/json",
    }
    try:
        response: requests.Response = requests.post(
            url=token_url, json=payload, headers=headers
        )
        response.raise_for_status()
        token_data: Any = response.json()
        return token_data["access_token"]

    except requests.exceptions.HTTPError as e:
        print(f"Token Exchange Error: {e}")
        if response.headers and response.content:  # type: ignore
            try:
                error_data: Any = response.json()  # type: ignore
                print(f"API Error details: {error_data}")
            except:
                print("Cannot parse error details")
        return None  # Return None to indicate failure to get token
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def download_mapillary_data(
    min_lon,
    min_lat,
    max_lon,
    max_lat,
    output_dir,
    csv_dir,
    limit=cfgs["LIMIT"],
    max_retries=cfgs["MAX_TRIES"],
) -> Any:
    """Downloads Mapillary images and metadata for a given bounding box with retries."""
    print("=" * 100)
    print(f'Processing: {cfgs["COUNTRY"]["REGION"]["NAME"]}')
    print("=" * 100)
    global ACCESS_TOKEN
    os.makedirs(name=output_dir, exist_ok=True)
    os.makedirs(name=csv_dir, exist_ok=True)

    bbox: str = f"{min_lon},{min_lat},{max_lon},{max_lat}"
    # These are all fields to put it

    all_fields_str = "id,altitude,atomic_scale,camera_parameters,camera_type,captured_at,compass_angle,computed_altitude,computed_compassangle,computed_geometry,computed_rotation,creator,exif_orientation,geometry,height,is_pano,make,model,thumb_original_url,merge_cc,mesh,sequence,sfm_cluster,width"

    # The base URL
    base_url: str = f"{cfgs["BASE_URL"]}" f"bbox={bbox}&" f"fields={all_fields_str}"
    url = f"{base_url}&limit={limit}"

    print(
        f"Downloading for Bounding Box: {bbox} | {cfgs["COUNTRY"]['REGION']["NAME"]}."
    )
    headers: dict[str, str] = {"Authorization": f"OAuth {ACCESS_TOKEN}"}

    # Prepare CSV headers
    csv_headers: Any = cfgs.get("CSV_HEADERS", [])  # Get headers from config

    csv_file: str = os.path.join(
        csv_dir, f"{cfgs['COUNTRY']['REGION']['NAME']}_metadata.csv"
    )  # Set metadata to other path

    with open(file=csv_file, mode="a", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.DictWriter(f=csvfile, fieldnames=csv_headers)
        csvwriter.writeheader()

        retries = 0
        while url and retries < max_retries:
            try:
                response: requests.Response = requests.get(url=url, headers=headers)
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

                data: Any = response.json()

                if "data" not in data:
                    print(
                        f"No images found in this bounding box | {cfgs["COUNTRY"]['REGION']["NAME"]}."
                    )
                    break

                for image in data["data"]:
                    image_id: Any = image["id"]

                    # Use requests to download the image
                    try:
                        thumb_url: Any = image.get(
                            "thumb_original_url"
                        )  # Retrieve thumbnail URL
                        if thumb_url:
                            image_response: requests.Response = requests.get(
                                url=thumb_url
                            )
                            image_response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

                            thumb_filepath: str = os.path.join(
                                output_dir, f"{image_id}.jpg"
                            )
                            with open(
                                file=thumb_filepath, mode="wb"
                            ) as imgfile:  # Open in binary write mode
                                imgfile.write(image_response.content)
                            print(f"Image Downloaded | {image_id}")

                    except requests.exceptions.RequestException as e:
                        print(f"Error downloading image | {image_id} | {e}")

                    row: dict[str, Any] = {
                        "id": image_id,
                        "altitude": image.get("altitude", ""),
                        "atomic_scale": image.get("atomic_scale", ""),
                        "camera_parameters": image.get("camera_parameters", ""),
                        "camera_type": image.get("camera_type", ""),
                        "captured_at": image.get("captured_at", ""),
                        "compass_angle": image.get("compass_angle", ""),
                        "computed_altitude": image.get("computed_altitude", ""),
                        "computed_compassangle": image.get("computed_compassangle", ""),
                        "computed_geometry": image.get("computed_geometry", {}),
                        "computed_rotation": image.get("computed_rotation", ""),
                        "exif_orientation": image.get("exif_orientation", ""),
                        "geometry": image.get("geometry", {}),
                        "height": image.get("height", ""),
                        "is_pano": image.get("is_pano", ""),
                        "make": image.get("make", ""),
                        "model": image.get("model", ""),
                        "thumb_original_url": image.get("thumb_original_url", ""),
                        "merge_cc": image.get("merge_cc", ""),
                        "mesh_id": image.get("mesh", {}).get("id", ""),
                        "mesh_url": image.get("mesh", {}).get("url", ""),
                        "sequence": image.get("sequence", ""),
                        "sfm_cluster_id": image.get("sfm_cluster", {}).get("id", ""),
                        "sfm_cluster_url": image.get("sfm_cluster", {}).get("url", ""),
                        "width": image.get("width", ""),
                    }
                    csvwriter.writerow(rowdict=row)
                    print(f"Metadata saved for image | {image_id} | in CSV")

                # Handle pagination (using the after parameter)
                if (
                    "paging" in data
                    and "cursors" in data["paging"]
                    and "after" in data["paging"]["cursors"]
                ):
                    after_cursor: Any = data["paging"]["cursors"]["after"]

                    url: str = (
                        f"{base_url}"
                        f"&access_token={ACCESS_TOKEN}"
                        f"&after={after_cursor}"
                        f"&limit={limit}"
                    )

                    print(f"Getting next page: {url}")

                else:
                    url = None  # type: ignore # No more pages
                retries = 0  # Reset retries on success

            except requests.exceptions.HTTPError as e:
                print(f"HTTP Error: {e}")
                if response.headers and response.content:  # type: ignore
                    try:
                        error_data: Any = response.json()  # type: ignore
                        print(f"API Error details: {error_data}")
                    except:
                        print("Cannot parse error details")

                if e.response.status_code == 429:
                    print("Rate limit hit. Waiting and retrying...")
                    time.sleep(60)  # Wait for a longer duration
                else:
                    print(f"Unrecoverable error.  Stopping after {retries} retries.")
                    break  # Break if it's not a rate limit issue
            except Exception as e:
                print(f"An error occurred: {e}")
                break


def main() -> None:
    """Main function to orchestrate the download process."""
    # Use the global keyword
    global ACCESS_TOKEN

    if ACCESS_TOKEN is None:
        authorization_code: str = get_authorization_code()
        if authorization_code:
            ACCESS_TOKEN = get_access_token(authorization_code=authorization_code)
            if ACCESS_TOKEN:
                print("Successfully obtained access token.")
            else:
                print("Failed to obtain access token.")
                exit()
        else:
            print("Authorization failed.")

    # Now check that ACCESS_TOKEN has some value
    if ACCESS_TOKEN:
        download_mapillary_data(
            min_lon=cfgs["COUNTRY"]["REGION"]["MIN_LON"],
            min_lat=cfgs["COUNTRY"]["REGION"]["MIN_LAT"],
            max_lon=cfgs["COUNTRY"]["REGION"]["MAX_LON"],
            max_lat=cfgs["COUNTRY"]["REGION"]["MAX_LAT"],
            output_dir=OUTPUT_DIRECTORY,
            csv_dir=CSV_DIRECTORY,
            limit=cfgs["LIMIT"],
            max_retries=cfgs["MAX_TRIES"],
        )
    else:
        print("Cannot start data download with an invalid access token.")


# Run main function
if __name__ == "__main__":
    main()


# uv run python ./data_collection/by_Maz/get_data.py
