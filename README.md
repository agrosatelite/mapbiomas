Install Google Cloud SDK

https://cloud.google.com/sdk/docs/#deb

```
$ export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)"
$ echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
$ curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
$ sudo apt-get update && sudo apt-get install google-cloud-sdk
$ gcloud init 
$ gcloud auth application-default login
```

Install python libraries

https://cloud.google.com/storage/docs/reference/libraries#client-libraries-install-python

```
$ pip install --upgrade google-cloud-storage
$ earthengine authenticate
```

Install postgres 9.5:
```
$ sudo apt-get install postgresql-9.5 postgresql-server-dev-9.5
$ sudo -u postgres psql
$ \password postgres
```

Create a database
```
$ psql -U postgres -W -h localhost
$ create database mapbiomas;
```

Create a virtual environment
```
$ virtualenv env
$ source env/bin/activate
```

Install requirements
```
$ pip install -r rsgee/requirements.txt
```

Initialize database:
```
>> from rsgee.db import DatabaseManager
>> db = DatabaseManager()
>> db.migrate()
```

To use client API, install ImageTk

```
sudo apt-get install python-imaging-tk
```
and alter in ee/mapclient.py from

```
import ImageTk
import Image
```

to

```
from PIL import ImageTk
from PIL import Image
```

Create your settings or use an existing, change "mapbiomas/settings/__init__.py" to choose the settings.
