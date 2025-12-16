import click

import src as bioflow_insight_src
from src.workflow import Workflow
from src.bioflowinsighterror import BioFlowInsightError

import sys

sys.setrecursionlimit(5000)


@click.command()
@click.version_option(bioflow_insight_src.__version__)
@click.argument('main_workflow_path')
@click.option(
    '--output-dir',
    default='./results',
    help='Where the results will be written.',
)
@click.option(
    '--duplicate',
    'duplicate',
    required=False,
    default=True,
    is_flag=True,
    help=''
    'When processes and subworkflows are duplicated in the workflow by the \'include as\' option, '
    'this option will duplicate the task in the graph output.',
)
@click.option(
    '--no-render-graphs',
    'render_graphs',
    required=False,
    default=True,
    is_flag=True,
    help='Don\'t generate the graphs output in png format using graphviz (faster),'
    'the mermaid and dot formats are always generated.',
)
@click.option(
    '--analysis',
    'analysis',
    type=click.STRING,
    required=False,
    help='todo',
    default='bioflow',
)
@click.option(
    '--name',
    'name',
    required=False,
    help='Workflow name, extracted otherwise (in the case of a Git repo).',
)
@click.option(
    '--display-info',
    'display_info',
    required=False,
    default=True,
    is_flag=True,
    help='Option to show a visual summary of the analysis.',
)
def cli_command(main_workflow_path, **kwargs):
    return cli(main_workflow_path, **kwargs)


def cli(main_workflow_path, render_graphs: bool, **kwargs):
    """
    The path to main file, subworkflows and modules must be in direct subdir of this file,
    in folders with eponymous names.
    """
    try:
        analysis = kwargs["analysis"]
        kwargs.pop("analysis")
    except:
        analysis = "bioflow"
    if analysis == "bioflow":
        w = Workflow(file=main_workflow_path, **kwargs)
        w.initialise_with_bioflow()
        w.generate_specification_graph()
        w.generate_process_dependency_graph()
        w.get_metro_map_json(render_dot=True)
        w.get_rocrate()

    elif analysis == "metroflow":
        try:
            w = Workflow(file=main_workflow_path, **kwargs)
            w.initialise()
            w.get_metro_map_json(render_dot=True)
        except BioFlowInsightError as e:
            raise Exception(str(e))
        except:
            raise Exception(
                "The Nextflow Language Server has detected an error in the workflow. Trying opening it with VSCode with the Nextflow plugin to fix it."
            )
    else:
        raise Exception('Unvalid value for "analysis" parameter. Either "bioflow-insight" or "metroflow"')


if __name__ == '__main__':
    cli_command()
