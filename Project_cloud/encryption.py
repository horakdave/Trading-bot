import base64
import requests
import os
from pydub import AudioSegment
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def encode_file(file_path):
    with open(file_path, 'rb') as f:
        file_data = f.read()
        base64_data = base64.b64encode(file_data)
        return base64_data

def decode_file(base64_data, output_path):
    with open(output_path, 'wb') as f:
        decoded_data = base64.b64decode(base64_data)
        f.write(decoded_data)

def upload_file(file_path, title, description, keyword, category_id):
    api_service_name = 'youtube'
    api_version = 'v3'
    youtube = build(api_service_name, api_version, developerKey=os.environ['DEVELOPER_KEY'])    #replace the DEVELOPER_KEY

    try:
        body = dict()
        body['snippet'] = dict()
        body['snippet']['title'] = title
        body['snippet']['description'] = description
        body['snippet']['tags'] = keyword
        body['snippet']['categoryId'] = category_id
        body['status'] = dict()
        body['status']['privacyStatus'] = 'public'

        file_path = file_path
        file_size = os.path.getsize(file_path)
        media = MediaFileUpload(file_path, mimetype='video/mp4', resumable=True)
        media.chunksize = 262144 * 4

        request = youtube.videos().insert(
            part=",".join(list(body.keys()) + ["status"]),
            body=body,
            media_body=media)

        response = None
        while response is None:
            status, response = request.next_chunk()
            print("Uploaded %d%%." % int(status.progress() * 100))

        print("Video successfully uploaded!")

    except HttpError as e:
        print("An error occurred: %s" % e)

if __name__ == '__main__':
    file_path = 'input_file.mp4'
    base64_data = encode_file(file_path)

    temp_file = 'temp_file.mp4'
    decode_file(base64_data, temp_file)

    upload_file(temp_file, 'My Title', 'My Description', 'keyword', '22')