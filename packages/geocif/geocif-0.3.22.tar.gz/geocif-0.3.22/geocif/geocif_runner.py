import os
import ast
import multiprocessing as mp
from pathlib import Path

from tqdm import tqdm
import matplotlib.pyplot as plt

from geocif import logger as log
from .ml import output
from geocif import geocif

plt.style.use("default")


def _loop_execute(logger, parser, project_name, country, crop, season, model, index):
    """

    Args:
        logger:
        parser:
        project_name:
        country:
        crop:
        season:
        model:
        index:

    Returns:

    """
    obj = geocif.Geocif(logger=logger, parser=parser, project_name=project_name)
    obj.read_data(country, crop, season)

    # Store config file in database, only execute this for
    # the first iteration of the loop
    if index == 0:
        output.config_to_db(obj.db_path, obj.parser, obj.today)

    # Setup metadata and run ML code
    obj.setup(season, model)
    if obj.simulation_stages:
        obj.execute()


def loop_execute(inputs):
    """

    Args:
        inputs:

    Returns:

    """
    enable_pycallgraph = False
    project_name, country, crop, season, model, logger, parser, index = inputs

    logger.info("=====================================================")
    logger.info(f"\tStarting GEOCIF: {country} {crop} {season} {model}")
    logger.info("=====================================================")

    if enable_pycallgraph:
        import warnings
        warnings.simplefilter(action="ignore", category=FutureWarning)

        from pycallgraph2 import Config, PyCallGraph, GlobbingFilter
        from pycallgraph2.output import GraphvizOutput

        graphviz = GraphvizOutput()
        graphviz.output_file = "geocif_visualization.png"
        plt.rcParams["figure.dpi"] = 600
        config = Config(max_depth=5)
        config.trace_filter = GlobbingFilter(
            exclude=[
                "pycallgraph.*",
            ]
        )

        with PyCallGraph(output=graphviz, config=config):
            _loop_execute(
                logger, parser, project_name, country, crop, season, model, index
            )
    else:
        _loop_execute(logger, parser, project_name, country, crop, season, model, index)


def gather_inputs(parser):
    """

    Args:
        parser:

    Returns:

    """
    project_name = parser.get("DEFAULT", "project_name")
    countries = ast.literal_eval(parser.get("DEFAULT", "countries"))

    """ Create a list of parameters over which to run the model"""
    all_inputs = []
    for country in countries:
        for crop in ast.literal_eval(parser.get(country, "crops")):
            for season in ast.literal_eval(parser.get(country, "forecast_seasons")):
                for model in ast.literal_eval(parser.get(country, "models")):
                    all_inputs.append([project_name, country, crop, season, model])

    return all_inputs


def execute_models(inputs, logger, parser):
    """
    Executes the model either in parallel or serially based on configuration.

    Args:
        inputs (list): The input data for model execution.
        logger (logging.Logger): Logger for tracking execution details
        parser (configparser.ConfigParser): Configuration file parser

    Returns:

    """
    do_parallel = parser.getboolean("DEFAULT", "do_parallel")

    # Add logger and parser to each element in inputs
    inputs = [item + [logger, parser, idx] for idx, item in enumerate(inputs)]

    if do_parallel:
        fraction_cpus = parser.getfloat("DEFAULT", "fraction_cpus")
        cpu_count = int(mp.cpu_count() * fraction_cpus)

        with mp.Pool(cpu_count) as pool:
            pool.map(loop_execute, inputs)
    else:
        for inputs in tqdm(inputs, desc="Executing ML models"):
            loop_execute(inputs)

    logger.info("======================================")
    logger.info("\tCompleted all model executions")
    logger.info("======================================")


def main(logger, parser):
    """

    Args:
        logger:
        parser:

    Returns:

    """
    inputs = gather_inputs(parser)
    execute_models(inputs, logger, parser)


def run(path_config_files=[Path("../config/geocif.txt")]):
    logger, parser = log.setup_logger_parser(path_config_files)
    main(logger, parser)


if __name__ == "__main__":
    run()
