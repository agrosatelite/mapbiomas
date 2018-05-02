from google.cloud import storage

class CloudStorage(object):
    def __init__(self):
        self.__storage_client = storage.Client()

    def create(self, bucket_name):
        bucket = self.__storage_client.create_bucket(bucket_name)
        print('Bucket {0} created'.format(bucket_name))

    def delete(self, bucket_name, blob_name=False):
        bucket = self.__storage_client.get_bucket(bucket_name)
        if blob_name:
            blob = bucket.blob(blob_name)
            blob.delete()
            print('Blob {0} deleted.'.format(blob_name))
        else:
            bucket.delete()
            print('Bucket {0} deleted'.format(bucket_name))

    def copy(self, bucket_name, blob_name, new_bucket_name, new_blob_name):
        source_bucket = self.__storage_client.get_bucket(bucket_name)
        source_blob = source_bucket.blob(blob_name)
        destination_bucket = self.__storage_client.get_bucket(new_bucket_name)
        new_blob = source_bucket.copy_blob(source_blob, destination_bucket, new_blob_name)
        print('Blob {0} in bucket {1} copied to blob {2} in bucket {3}.'.format(source_blob.name, source_bucket.name, new_blob.name,
                                                                                destination_bucket.name))

    def rename(self, bucket_name, blob_name, new_name):
        bucket = self.__storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        new_blob = bucket.rename_blob(blob, new_name)
        print('Blob {0} has been renamed to {1}'.format(blob.name, new_blob.name))

    def upload(self, bucket_name, source_file_name, destination_blob_name):
        bucket = self.__storage_client.get_bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        print('File {0} uploaded to {1}.'.format(source_file_name, destination_blob_name))

    def download(self, bucket_name, source_blob_name, destination_file_name):
        bucket = self.__storage_client.get_bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
        print('Blob {0} downloaded to {1}.'.format(source_blob_name, destination_file_name))

    def list(self, bucket_name, filter=None):
        bucket = self.__storage_client.get_bucket(bucket_name)

        blobs = bucket.list_blobs()
        blobs_list = []
        for blob in blobs:
            if filter and blob.name.find(filter) == -1:
                continue
            blobs_list.append(blob.name)
        return blobs_list