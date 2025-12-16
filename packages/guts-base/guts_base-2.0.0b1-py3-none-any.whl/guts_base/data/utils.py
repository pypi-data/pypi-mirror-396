import warnings

def datalad_locked_file_warning(file):
    warnings.warn(
        f"The file '{file}' does not have write access. "
        f"To unlock the file, use DataLad with the command: "
        f"datalad unlock '{file}'."
    )