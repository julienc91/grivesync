grivesync
=========

Backup a folder with your Google Drive account from the command line.

* Author: Julien CHAUMONT (https://julienc.io)
* Version: 1.0
* Date: 2014-09-25
* Licence: GPL v2
* Url: http://github.io/julienc91/grivesync
* Python version: 2.7

## Requirements

### Python packages

`google-api-python-client` and `python-magic` are required. They can
be installed using `pip`:

    pip install google-api-python-client
    pip install python-magic

    
### Google API credentials

You will need to create a project under Google Developers in order to
get access to the Google Drive API. To do so, go to:

https://console.developers.google.com/project

Then, create a new project, with the name and project id you
want. Wait for the creation process to finish, then go to 'APIs &
auth' and 'APIs' on the left panel. You can disable all the already
enabled APIs, but enable the 'Drive API'.

Then go to 'Credentials' and 'Create a new Client ID' for
Oauth. Select 'Installed application' and 'Other' for the platform.

Finally, copy and paste the 'Client ID' and the 'Client Secret' into the
'settings.py' file.


## Usage

grivesync is meant to backup a single folder. What you can do is
create a 'backup' folder somewhere in your filesystem, and create
symbolic links of everything you want to backup.

For instance:

    $> mkdir /home/backup
    $> ln -s /var/log /home/backup/var_log
    $> ln -s /etc/nginx/sites-available /home/backup/nginx_conf
    
Then, simply run grivesync:

    $> python grivesync.py /home/backup
    
It will create a folder in your Google Drive called
'grivesync_YYYYMMDD-HHMMSS' where you will find the complete backup of
your local folder (subfolders are included).


## Improvements

For the moment, grivesync does not delete old backups, and upload all
the files every time without checking for changes. There is also no
exclude list. These features might come in a near future however.
