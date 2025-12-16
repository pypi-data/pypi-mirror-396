import click
from agilicus.output.table import make_columns
from agilicus.output.table import output_entry
from agilicus.output.table import format_table
from agilicus.command_helpers import Command
from . import deployments


cmd = Command()


@cmd.command(name="list-deployments")
@click.option("--limit", default=500)
@click.option("--org-id", default=None)
@click.pass_context
def cli_command_list_deployments(ctx, **kwargs):
    results = deployments.list_deployments(ctx, **kwargs)
    columns = make_columns(
        ctx,
        results,
        """
          - metadata.id(newname=id)
          - spec.name(newname=name)
          - status.parameters:
            - name
            - type
          - status.schema_errors
        """,
    )
    print(format_table(ctx, results, columns))


@cmd.command(name="get-deployment")
@click.argument("deployment-id")
@click.option("--org-id", default=None)
@click.pass_context
def cli_command_get_deployment(ctx, **kwargs):
    result = deployments.get_deployment(ctx, **kwargs)
    output_entry(ctx, result.to_dict())


@cmd.command(name="delete-deployment")
@click.argument("deployment-id")
@click.option("--org-id", default=None)
@click.pass_context
def cli_command_delete_deployment(ctx, **kwargs):
    deployments.delete_deployment(ctx, **kwargs)


@cmd.command(name="add-deployment")
@click.argument("name")
@click.option("--schema", type=click.Path(exists=True))
@click.option("--schema-name", default=None)
@click.option("--org-id", default=None)
@click.option("--description", default=None)
@click.pass_context
def cli_command_add_deployment(ctx, **kwargs):
    result = deployments.add_deployment(ctx, **kwargs)
    output_entry(ctx, result.to_dict())


@cmd.command(name="list-deployment-instances")
@click.option("--limit", default=500)
@click.option("--org-id", default=None)
@click.pass_context
def cli_command_list_deployment_instances(ctx, **kwargs):
    results = deployments.list_deployment_instances(ctx, **kwargs)
    columns = make_columns(
        ctx,
        results,
        """
          - metadata.id(newname=id)
          - spec.name(newname=name)
          - spec.inputs:
            - name
            - value_as_string
          - status.status
          - status.resources:
            - template_name
            - name
            - id
            - type
            - shared
        """,
    )
    print(format_table(ctx, results, columns))


@cmd.command(name="get-deployment-instance")
@click.argument("deployment-instance-id")
@click.option("--org-id", default=None)
@click.pass_context
def cli_command_get_deployment_instance(ctx, **kwargs):
    result = deployments.get_deployment_instance(ctx, **kwargs)
    output_entry(ctx, result.to_dict())


@cmd.command(name="delete-deployment-instance")
@click.argument("deployment-instance-id")
@click.option("--org-id", default=None)
@click.pass_context
def cli_command_delete_deployment_instance(ctx, **kwargs):
    deployments.delete_deployment_instance(ctx, **kwargs)


@cmd.command(name="list-deployment-templates")
@click.option("--limit", default=500)
@click.option("--org-id", default=None)
@click.option("--system-templates", default=True)
@click.option("--template-type", default=None)
@click.pass_context
def cli_command_list_deployment_templates(ctx, **kwargs):
    results = deployments.list_deployment_templates(ctx, **kwargs)
    columns = make_columns(
        ctx,
        results,
        """
          - metadata.id(newname=id)
          - spec.org_id(newname=org_id)
          - spec.name(newname=name)
          - spec.template_type(newname=template_type)
        """,
    )
    print(format_table(ctx, results, columns))


@cmd.command(name="add-deployment-instance")
@click.argument("deployment-id")
@click.argument("name")
@click.option("--org-id", default=None)
@click.option("--description", default=None)
@click.option("--input", multiple=True)
@click.pass_context
def cli_command_add_deployment_instance(ctx, **kwargs):
    result = deployments.add_deployment_instance(ctx, **kwargs)
    output_entry(ctx, result.to_dict())


@cmd.command(name="get-deployment-template")
@click.argument("deployment-template-id")
@click.option("--org-id", default=None)
@click.pass_context
def cli_command_get_deployment_template(ctx, **kwargs):
    result = deployments.get_deployment_template(ctx, **kwargs)
    output_entry(ctx, result.to_dict())


@cmd.command(name="add-deployment-template")
@click.argument("name")
@click.argument("template-type", type=click.Choice(["model", "schema"]))
@click.argument("template", type=click.Path(exists=True))
@click.option("--org-id", default=None)
@click.option("--description", default=None)
@click.pass_context
def cli_command_add_deployment_template(ctx, **kwargs):
    result = deployments.add_deployment_template(ctx, **kwargs)
    output_entry(ctx, result.to_dict())


@cmd.command(name="update-system-templates")
@click.argument("templates", type=click.Path(exists=True))
@click.option("--org-id", default=None)
@click.pass_context
def cli_command_update_system_templates(ctx, **kwargs):
    if not ctx.obj.get("ADMIN_MODE"):
        print("must run in --admin mode")
        return
    deployments.update_system_templates(ctx, **kwargs)


@cmd.command(name="delete-deployment-template")
@click.argument("deployment-template-id")
@click.option("--org-id", default=None)
@click.pass_context
def cli_command_delete_deployment_template(ctx, **kwargs):
    deployments.delete_deployment_template(ctx, **kwargs)


def add_commands(cli):
    cmd.add_to_cli(cli)
