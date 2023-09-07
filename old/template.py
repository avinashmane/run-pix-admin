##
## https://developers.google.com/slides/api/quickstart/python

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import dotenv
dotenv.load_dotenv()
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/presentations.readonly"]

# The ID of a sample presentation.
PRESENTATION_ID = "1EAYk18WDjIG-zp_0vLm3CsfQh_i8eXc67Jo2O9C6Vuc"

service_account = json.loads(os.environ['SA']) 
print(service_account)

def main():
  """Shows basic usage of the Slides API.
  Prints the number of slides and elements in a sample presentation.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("slides", "v1", credentials=creds)

    # Call the Slides API
    presentation = (
        service.presentations().get(presentationId=PRESENTATION_ID).execute()
    )
    slides = presentation.get("slides")

    print(f"The presentation contains {len(slides)} slides:")
    for i, slide in enumerate(slides):
      print(
          f"- Slide #{i + 1} contains"
          f" {len(slide.get('pageElements'))} elements."
      )
  except HttpError as err:
    print(err)


if __name__ == "__main__":
  main()