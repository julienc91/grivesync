#!/usr/bin/python

import os
import httplib2
import datetime
import magic
import settings
import sys

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow


# Oauth settings
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


##
# Oauth management
# Adapted from:
# https://developers.google.com/drive/web/quickstart/quickstart-python
#
def connect_gdrive():

    # Run through the OAuth flow and retrieve credentials
    flow = OAuth2WebServerFlow(settings.CLIENT_ID, settings.CLIENT_SECRET,
                               OAUTH_SCOPE, REDIRECT_URI)
    authorize_url = flow.step1_get_authorize_url()
    print 'Go to the following link in your browser: ' + authorize_url
    code = raw_input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)

    # Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    http = credentials.authorize(http)
    drive_service = build('drive', 'v2', http=http)

    return drive_service


##
# Backup the given folder on Google Drive
# @param drive_service   returned by the connect_gdrive function
# @param root            path to the folder to backup
#
def sync(drive_service, root):

    ##
    # Create a subfolder on Google Drive
    # @param folder_name       name of the folder to create
    # @param parent_folder_id  gdrive id of the parent folder
    #                          if None, the folder will be created at
    #                          Gdrive's root
    #
    def create_folder(folder_name, parent_folder_id=None):

        print "Creating folder " + folder_name
        body = {
            'title': folder_name,
            'mimeType': "application/vnd.google-apps.folder"}
        if parent_folder_id:
            body["parents"] = [{"id": parent_folder_id}]
        folder = drive_service.files().insert(body=body).execute()
        # Return the newly created folder's gdrive id
        return folder["id"]

    ##
    # Backup a file
    # @param file_path         path to the file to backup
    # @param parent_folder_id  gdrive id of the parent folder
    #
    def upload_file(file_path, parent_folder_id):

        print "Uploading file " + file_path
        mimetype = magic.from_file(file_path, mime=True)
        if not mimetype:
            mimetype = 'application/octet-stream'
        media_body = MediaFileUpload(file_path, mimetype=mimetype)
        body = {
            'title': os.path.basename(file_path),
            'mimeType': mimetype,
            'parents': [{"id": parent_folder_id}]}
        drive_service.files().insert(body=body,
                                     media_body=media_body).execute()

    ##
    # Backup a folder recursively
    # @param folder_path       path to the folder to backup
    # @param parent_folder_id  gdrive id of the parent folder
    #
    def sync_folder(folder_path, parent_folder_id):

        l = os.listdir(folder_path)
        for filename in l:
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                try:
                    upload_file(file_path, parent_folder_id)
                except KeyboardInterrupt:
                    sys.exit("Exiting on user request")
                except:
                    print "An error occured, retrying"
                    print "A second error will stop the backup operation"
                    upload_file(file_path, parent_folder_id)
            else:
                folder_id = create_folder(filename, parent_folder_id)
                sync_folder(file_path, folder_id)

    # Initially create a folder where the backup will be moved
    backup_folder_name = ("grivesync_" +
                          datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup_folder_id = create_folder(backup_folder_name)
    # And start the backup operation
    sync_folder(root, backup_folder_id)


##
# Print usage and exit
def usage():
    sys.exit("Usage: %s <path>" % sys.argv[0])


if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
    root = sys.argv[1]

    if not os.path.isdir(root):
        usage()

    drive_service = connect_gdrive()
    sync(drive_service, root)
