import chardet
import os
import sqlite3
import pandas as pd
import string

class FileLoader:
    '''
    Class to load file(s) from xlsx and csv into sql db.
    '''

    def __init__(self, path: str) -> None:
        '''
        Constructor for LoadFile class.

        Initializes attributes:
        - number_of_files: Number of files found.
        - file_info: Dictionary to store file information.
        '''
        self.path_to_data = path
        self.number_of_files = 0
        self.file_info = {}
        self.failed_files = set()
        self.database_name = None

        self._get_all_files()

    def detect_encoding(self, file_path: str) -> str:
        """
        Detect the encoding of a file.
        """
        try:
            with open(file_path, 'rb') as file:
                # Read the first 1024 bytes of the file
                raw_data = file.read(1024)
                result = chardet.detect(raw_data)
                first_att = result['encoding']
                if first_att == None:
                    return self._try_find_encoding(file_path)
                else:
                    return first_att
        except PermissionError as err:
            return PermissionError(f"File {err.filename} inaccessable. Close the file and rerun the program.")

    def _try_find_encoding(self, file_path: str, encodings: list = ['utf-8', 'latin-1', 'ascii']) -> str:
        """
        Detect the encoding of a file by trying multiple encodings.
        """
        with open(file_path, 'rb') as file:
            raw_data = file.read(1024)
            for encoding in encodings:
                try:
                    decoded_data = raw_data.decode(encoding)
                    return encoding
                except UnicodeDecodeError:
                    continue
        return 'utf-8'

    def _get_all_files(self) -> None:
        '''
        Retrieves all files in the specified directory.

        Args:
        - path_to_data: A string representing the path to the directory containing the files.
        '''
        files = os.listdir(self.path_to_data)
        self.number_of_files = len(files)
        for file in files:
            file_path = os.path.join(self.path_to_data, file)
            file_info = FileInfo(file_path, self.get_file_size(
                file_path), self.detect_encoding(file_path))
            self.file_info[file] = file_info

    def add_files(self, path_to_data: str) -> None:
        files = os.listdir(path_to_data)
        self.number_of_files = len(files)
        for file in files:
            file_path = os.path.join(path_to_data, file)
            file_info = FileInfo(file_path, self.get_file_size(
                file_path), self.detect_encoding(file_path))
            self.file_info[file] = file_info

    def get_file_size(self, path_to_file: str) -> int:
        '''
        Returns the size of a file in bytes.

        Args:
        - path_to_file: A string representing the path to the file.

        Returns:
        An integer representing the size of the file in bytes.
        '''
        return os.path.getsize(path_to_file)

    def display_file_info(self):
        for key, val in self.file_info.items():
            print(
                f"File name: {key}\nFull path: {val.path}\nSize: {val.size} bytes\nEncoding: {val.encoding}\n\n")

    def create_db(self, db_name: str = "old_files.db") -> None:
        '''
        Reads files into SQLite database.
        Accepted File Formats:
            - Single-tab Excel files (.xlsx)
            - Comma Seperated Value files (.csv)
        '''
        print("Initializing database...")
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()

        for file, info in self.file_info.items():
            print(f"Adding {file} to database.")

            # Extracting file name without extension and cleaning it from special characters
            sanitized_file = ''.join(char for char in os.path.splitext(
                file)[0] if char.isalnum() or char in string.whitespace)

            try:
                # Load file into DataFrame
                extension = info.path.split(".")[-1]
                if extension == "csv":
                    df = pd.read_csv(info.path)
                elif extension == "json":
                    df = pd.read_json(info.path)
                else:
                    df = pd.read_excel(info.path)

                # Save DataFrame to SQLite database
                df.to_sql(name=sanitized_file, con=self.conn,
                          if_exists='replace', index=False)

                print(
                    f"Successfully added {file} to database as table {sanitized_file}.")
            except Exception as e:
                print(f"Error processing {file}: {e}")

        self.conn.commit()
        self.cur.close()
        self.conn.close()
        self.database_name = db_name
        print("Database connection closed.")

    def update_db(self, path_to_file: str) -> None:
        if self.database_name == None:
            return Exception("No database available to update.\nCall FileLoader.create_db() first.")
        self.file_info[path_to_file.split("/")[-1]] = FileInfo(path_to_file, self.get_file_size(
            path_to_file), self.detect_encoding(path_to_file))
        print("Updating database...\n")
        self.conn = sqlite3.connect(self.database_name)
        ext = path_to_file.split(".")[-1]
        sanitized_file = ''.join(char for char in os.path.splitext(
            path_to_file)[0] if char.isalnum() or char in string.whitespace)

        if ext == "csv":
            pd.read_csv(path_to_file).to_sql(name=sanitized_file, con=self.conn,
                                             if_exists='replace', index=False)
        elif ext == "json":
            pd.read_csv(path_to_file).to_sql(name=sanitized_file, con=self.conn,
                                             if_exists='replace', index=False)
        else:
            pd.read_excel(path_to_file).to_sql(name=sanitized_file, con=self.conn,
                                               if_exists='replace', index=False)

        self.conn.close()
        print("Database connection closed.")

    def total_transfer_size(self) -> None:
        size = 0
        for k, v in self.file_info.items():
            size += v.size
        print(f"Total transfer size: {size} bytes.\n")


class FileInfo:
    def __init__(self, path: str, size: int, encoding: str) -> None:
        self.path, self.size, self.encoding = path, size, encoding
