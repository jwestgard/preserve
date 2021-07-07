def create_temp_file(temp_file_path, filename, contents):
    '''
    Creates a temporary file in the given path with the given filename
    and contents
    '''
    temp_file_path.mkdir(exist_ok=True)

    temp_file = temp_file_path / filename

    temp_file.write_text(contents)
    return temp_file
