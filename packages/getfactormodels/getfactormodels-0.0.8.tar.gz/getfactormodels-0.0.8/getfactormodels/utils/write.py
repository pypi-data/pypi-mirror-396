# PLACEHOLDER
#
# will be _Writer class.


# from utils


# TODO: Will redo as a Writer class with use pyarrow
# changing: no longer uses filename, output_dir, just filepath. Always returns Path 
def _prepare_filepath(filepath=None) -> Path:
    if filepath is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = Path.cwd() / f"data_{timestamp}.csv"
        print(f"No filepath provided, creating: {filepath.name}")
        return filepath
    
    filepath = Path(filepath).expanduser()
    
    if filepath.is_dir():
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = filepath / f"data_{timestamp}.csv"
        print(f"Directory provided, creating: {filepath.name}")
    
    return filepath

def _save_to_file(data, filepath=None):
    if not isinstance(data, (pd.DataFrame, pd.Series)):
            raise ValueError('Data is not a pandas DataFrame or Series')
    full_path = _prepare_filepath(filepath)
    
    if full_path is None:
        raise ValueError("Failed to prepare filepath")
    
    extension = full_path.suffix.lower()
 
    if full_path.is_file():
        print(f'File exists: {full_path.name} - overwriting...')

    try:
        if extension == '.txt':
            data.to_csv(str(full_path), sep='\t')
        elif extension == '.csv':
            data.to_csv(str(full_path))
        elif extension == '.xlsx':
            data.to_excel(str(full_path))
        elif extension == '.pkl':
            data.to_pickle(str(full_path))
       # elif extension == '.md':
       #    #.md removed for now 
        else:
            supported = ['.txt', '.csv', '.xlsx', '.pkl']
            raise ValueError(f'Unsupported file extension: {extension}. Must be one of: {supported}')

        print(f"File saved to: {full_path}")
    except Exception as e:
        raise IOError(f"Failed to save file to {full_path}: {str(e)}")
