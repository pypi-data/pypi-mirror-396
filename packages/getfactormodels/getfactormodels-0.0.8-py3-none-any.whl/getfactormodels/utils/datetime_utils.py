# placeholder
#


# from utils
def _validate_date(date_input):
    """Converts date formats to a standardized str format."""
    if date_input is None:
        return None

    # is a timestamp
    if isinstance(date_input, pd.Timestamp):
        return date_input.strftime("%Y-%m-%d")

    # is str input
    if isinstance(date_input, str):
        try:
            # cnvert to datetime
            return pd.to_datetime(date_input).strftime("%Y-%m-%d")
        except (ValueError, pd.errors.ParserError) as err:
            raise ValueError("Incorrect date format, use YYYY-MM-DD.") from err
    try:
        # already a dt object
        return date_input.strftime("%Y-%m-%d")
    except AttributeError:
        raise TypeError(f"Unsupported date type: {type(date_input)}")


def _slice_dates(data, start_date=None, end_date=None):
    """Slice the dataframe to the specified date range."""
    if start_date is None and end_date is None:
        return data

    if start_date is not None:
        start_date = _validate_date(start_date)
    if end_date is not None:
        end_date = _validate_date(end_date)

    start = _validate_date(start_date) if start_date else None
    end = _validate_date(end_date) if end_date else None

    if not isinstance(data.index, pd.DatetimeIndex):
        try:
            data.index = pd.to_datetime(data.index)
        except Exception as e:
            raise ValueError("error parsing dates") from e
    
    return data.loc[start:end]
