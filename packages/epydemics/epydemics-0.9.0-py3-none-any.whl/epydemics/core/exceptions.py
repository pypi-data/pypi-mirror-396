"""
Custom exceptions for the epydemics library.
"""


class EpydemicsError(Exception):


    """Base exception for the epydemics library."""





    pass








class NotDataFrameError(EpydemicsError):


    """Custom exception for when the input is not a Pandas DataFrame."""





    def __init__(self, message="Input data must be a pandas DataFrame"):


        super().__init__(message)








class DataValidationError(EpydemicsError):








    """Custom exception for data validation errors."""

















    def __init__(self, *args):








        if not args:








            super().__init__("Data validation failed")








        else:








            super().__init__(*args)

















class DateRangeError(EpydemicsError):


    """Custom exception for date range errors."""





    def __init__(self, message="Invalid date range"):


        super().__init__(message)




