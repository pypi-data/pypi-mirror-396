import os
from datetime import datetime, timezone
from io import BytesIO, FileIO
from time import sleep
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload, HttpError
from google_client.service import GoogleServiceMixin

folder_type = 'application/vnd.google-apps.folder'
default_file_fields = ('id, name, appProperties, webViewLink, size, modifiedTime, createdTime, '
                       'mimeType, owners, thumbnailLink, md5Checksum')


class FileNotFound(Exception):
    pass


class GoogleDrive(GoogleServiceMixin):

    api_name = 'drive'
    api_version = 'v3'
    scopes = ['https://www.googleapis.com/auth/drive']

    def __init__(self, credentials, account_email=None, root='root', shared_drive=None):
        super().__init__(credentials, account_email=account_email)
        self.root = root
        self.shared_drive = shared_drive
        if shared_drive and root == 'root':
            self.root = shared_drive

    @staticmethod
    def convert_time(t):
        utc_dt = datetime.strptime(t[:-1] + ' +0000', '%Y-%m-%dT%H:%M:%S.%f %z')
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None).replace(tzinfo=None)

    @classmethod
    def convert_dict_time(cls, file_dict, key):
        if key in file_dict:
            file_dict[key] = cls.convert_time(file_dict[key])

    def file_list(self, **kwargs):
        if 'fields' not in kwargs:
            kwargs['fields'] = f"nextPageToken, files({default_file_fields})"
        kwargs.update(dict(supportsAllDrives=True, includeItemsFromAllDrives=True))
        if self.shared_drive:
            kwargs.update(dict(corpora='drive', driveId=self.shared_drive))
        results = self.service.files().list(**kwargs, pageSize=50).execute()
        next_page = results.get('nextPageToken')
        items = results.get('files', [])
        while next_page:
            results = self.service.files().list(**kwargs, pageSize=50, pageToken=next_page).execute()
            next_page = results.get('nextPageToken')
            items = items + results.get('files', [])
        for i in items:
            self.convert_dict_time(i, 'modifiedTime')
            self.convert_dict_time(i, 'createdTime')
        return items

    @staticmethod
    def build_q(name=None, mime_type=None, folder=None, shared_with_me=None, trashed=False):
        if trashed is None:
            search = []
        else:
            search = [f'trashed = {str(trashed).lower()}']
        if name:
            search.append(f"name='{name}'")
        if mime_type:
            search.append(f"mimeType='{mime_type}'")
        if folder:
            if type(folder) == dict:
                search.append(f"'{folder['id']}' in parents")
            else:
                search.append(f"'{folder}' in parents")
        if shared_with_me:
            search.append('sharedWithMe')
        return ' and '.join(search)

    def get_folder(self, folder_path, shared_with_me=False, **kwargs):
        paths = folder_path.split('/')
        next_folder = None
        if shared_with_me:
            q_dict = {'shared_with_me': True}
        elif 'folder' in kwargs:
            q_dict = {'folder': kwargs.pop('folder')}
        else:
            q_dict = {'folder': self.root}
        for p in paths:
            q_dict.update({'mime_type': folder_type, 'name': p})
            next_folder = self.file_list(q=self.build_q(**q_dict), **kwargs)
            if not next_folder:
                return
            q_dict = {'folder': next_folder[0]}
        if next_folder and len(next_folder) > 0:
            return next_folder[0]

    def get_folder_id(self, folder_id, folder_path, folder):
        if folder_id:
            return folder_id
        if folder:
            return folder['id']
        return self.get_folder(folder_path)['id']

    def get_file(self, folder_id=None, folder_path=None, folder=None, file_name=None, file_id=None):
        if not file_id:
            folder_id = self.get_folder_id(folder_id, folder_path, folder)
            files = self.file_list(q=self.build_q(name=file_name, folder=folder_id))
            if not files:
                raise FileNotFound
            return files[0]
        else:
            return self.service.files().get(fileId=file_id, fields=default_file_fields,
                                            supportsAllDrives=True).execute()

    def get_file_contents(self, folder_id=None, folder_path=None, folder=None,
                          file_name=None, file_id=None,
                          local_folder=None):
        """
        One of the folder parameters must be supplied if file_id is not set
        :param folder_id: Google Drive folder id
        :param folder_path: Path separated by /
        :param folder: Folder dictionary with 'id' key as folder id

        :param file_name:
        :param file_id:

        :param local_folder: If set it will download the file to local drive and return the filename

        :return: if local folder the file name, otherwise a BytesIO stream
        """

        if not file_id:
            folder_id = self.get_folder_id(folder_id, folder_path, folder)
            files = self.file_list(q=self.build_q(name=file_name, folder=folder_id))
            if not files:
                raise FileNotFound
            file_id = files[0]['id']
            file_size = int(files[0]['size'])
        else:
            file_size = int(self.get_file(file_id=file_id)['size'])

        if local_folder:
            if not file_name:
                file_name = self.get_file(file_id=file_id)['name']
            fh = FileIO(os.path.join(local_folder, file_name), 'wb')
        else:
            fh = BytesIO()
        if file_size > 0:
            request = self.service.files().get_media(fileId=file_id, supportsAllDrives=True)
            downloader = MediaIoBaseDownload(fh, request, chunksize=1024*1024*10)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
        if local_folder:
            return file_name
        else:
            fh.seek(0)
            return fh

    def create_folder(self, title, parent):
        body = {'name': title, 'mimeType': folder_type}
        if parent:
            body['parents'] = [parent['id']]
        return self.service.files().create(body=body, fields='id', supportsAllDrives=True).execute()

    def find_create_folder(self, folder_path, **kwargs):
        folder = self.get_folder(folder_path, **kwargs)
        if folder:
            return folder
        if folder_path.find('/') < 0:
            parent_folder = kwargs['folder']
        else:
            parent_folder = self.find_create_folder(folder_path[0:folder_path.rfind('/')], **kwargs)
        self.create_folder(folder_path[folder_path.rfind('/') + 1:], parent_folder)
        sleep(5)
        return self.get_folder(folder_path, **kwargs)

    def create_file_body(self, body, data_stream):
        size = data_stream.seek(0, 2)
        data_stream.seek(0)
        if size == 0:
            google_file = self.service.files().create(body=body, supportsAllDrives=True).execute()
        else:
            if body.get('mimeType'):
                media_body = MediaIoBaseUpload(data_stream, mimetype=body['mimeType'], resumable=True)
            else:
                media_body = MediaIoBaseUpload(data_stream, resumable=True)
            try:
                google_file = self.google_execute_retry(self.service.files().create(body=body, media_body=media_body,
                                                                                    supportsAllDrives=True))
            except HttpError:
                self.service = self.get_service_account()
                google_file = self.service.files().create(body=body, media_body=media_body,
                                                          supportsAllDrives=True).execute()
        return google_file

    def create_file_stream(self, title, parent, data_stream, body=None, mime_type=None):
        if body is None:
            body = {}
        body['name'] = title
        if mime_type:
            body['mimeType'] = mime_type
        else:
            body['mimeType'] = '[*/*]'
        if parent:
            body['parents'] = [parent['id']]
        return self.create_file_body(body, data_stream)

    def create_file(self, title, parent, mime_type, data, body=None):
        return self.create_file_stream(title, parent, BytesIO(data), body=body, mime_type=mime_type)

    def get_all_descendants(self, folder_id):
        files_folders = self.file_list(q=self.build_q(folder=folder_id))
        output_files = []
        for f in files_folders:
            if f['mimeType'] == folder_type:
                descendant_files = self.get_all_descendants(f['id'])
                for d in descendant_files:
                    d['tags'] = d.get('tags', []) + [f['name']]
                output_files += descendant_files
            else:
                output_files.append(f)
        return output_files
