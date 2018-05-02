import os, sys

from cloud import CloudStorage

if len(sys.argv) < 2:
    print "Restart the script with more one parameter (filter)..."
    sys.exit(0)

DIR = os.path.dirname(os.path.abspath(__file__))
BUCKET = "agrosatelite-mapbiomas"

cloud = CloudStorage()

f = sys.argv[1]

for blob in cloud.list(BUCKET):
    if blob.find(f) != -1:
        file_output = "{0}/{1}".format(str(DIR), str(blob))
        if not os.path.exists(file_output):
            print "Downloading: {0}".format(blob)
            cloud.download(BUCKET, blob, file_output)
        else:
            print "File {0} exists!".format(file_output)
