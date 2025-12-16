# TODO: Set up data import pipelines and templates for importing data into expyDB
# TODO: Test plotting
# TODO: Run a simple test case with the ring test data
import pandas as pd
from datetime import datetime, timedelta
import tempfile
from click.testing import CliRunner
from guts_base.data import create_database_and_import_data, OpenGutsIO, time_of_death_to_openguts

def test_data_import_openguts():
    tempdir = tempfile.TemporaryDirectory()

    runner = CliRunner(echo_stdin=True)
    result = runner.invoke(
        create_database_and_import_data, 
        catch_exceptions=False,
        args=[
            "--datasets_path", "data/templates/ringtest_A_SD_openguts_notation.xlsx", 
            "--database_path", f"{tempdir.name}/ringtest.db", 
            "--preprocessing", "guts_base.data.preprocessing.ringtest",
            "--preprocessing-out", f"{tempdir.name}/processed_{{filename}}"
        ]
    )

    if isinstance(result.exception, SystemExit):
        raise KeyError(
            "Invokation of the click command did not execute correctly. " +
            f"Recorded output: {' '.join(result.output.splitlines())}"
        )
    
    else:
        print(result.output)

def test_data_import_time_of_death():
    tempdir = tempfile.TemporaryDirectory()
    runner = CliRunner(echo_stdin=True)
    result = runner.invoke(
        time_of_death_to_openguts, 
        catch_exceptions=False,
        args=[
            "--file", "data/templates/ringtest_A_SD_time_of_death_notation.xlsx", 
            "--sheet", "time-of-death", 
            "--out", tempdir.name,
            "-c", "exposure"
        ]
    )

    if isinstance(result.exception, SystemExit):
        raise KeyError(
            "Invokation of the click command did not execute correctly. " +
            f"Recorded output: {' '.join(result.output.splitlines())}"
        )
    
    else:
        print(result.output)
    
    # this will raise an assertion error if the data cannot be converted to
    # an experiment
    io = OpenGutsIO(f"{tempdir.name}/openguts_ringtest_A_SD_time_of_death_notation.xlsx")
    io.to_experiment()


def test_tod_to_openguts():
    """Tests only the conversion, there is no pre-processing template in place.
    This would have to be built.
    """
    tempdir = tempfile.TemporaryDirectory()
    runner = CliRunner(echo_stdin=True)
    result = runner.invoke(
        time_of_death_to_openguts, 
        catch_exceptions=False,
        args=[
            "--file", "data/templates/tktd_data_template_time_of_death_notation.xlsx", 
            "--sheet", "time-of-death",
            "--out", tempdir.name,
            "-c", "concentration_pesticide__mg/g",
            "-c", "concentration_pesticide_B__mg/g"
        ],
    )

    if isinstance(result.exception, SystemExit):
        raise KeyError(
            "Invokation of the click command did not execute correctly. " +
            f"Recorded output: {' '.join(result.output.splitlines())}"
        )
    
    else:
        print(result.output)
        
    
    processed_data = pd.read_excel(
        f"{tempdir.name}/openguts_tktd_data_template_time_of_death_notation.xlsx",
        sheet_name=None
    )

    pd.testing.assert_frame_equal(
        processed_data["concentration_pesticide__mg_g"],
        pd.DataFrame({
            "time [d]": [0, 1/24, 64],
            "01__1": [0,0,0],
            "02__2": [0,0,0],
        })
    )

    pd.testing.assert_frame_equal(
        processed_data["concentration_pesticide_b__mg_g"],
        pd.DataFrame({
            "time [d]": [0, 1/24, 64],
            "01__1": [0,0,0],
            "02__2": [0.5,0,0],
        })
    )


    pd.testing.assert_frame_equal(
        processed_data["survival"],
        pd.DataFrame({
            "time [d]":  list(range(65)),
            "01__1": [
                30,28,26,26,26,26,26,26,25,24,24,24,24,24,24,24,24,24,24,24,24,
                24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,
                24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,24,
                24,24],
            "02__2": [
                30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,27,27,27,26,26,25,
                25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,
                25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,
                25,24],
        })
    )

if __name__ == "__main__":
    test_data_import_time_of_death()
    test_tod_to_openguts()