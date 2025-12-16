import click
from tamu_id_minter import EZIDARKHandler
from tamu_id_minter.crossref import CrossrefDepositHandler

@click.group()
def cli() -> None:
    pass

@cli.command(
    "create_arks", help="Creates ARKs from a CSV with Metadata"
)
@click.option(
    "--input_csv",
    "-i",
    help="The path to the CSV including ARK metadata",
)
@click.option(
    "--output_csv",
    "-o",
    help="The path to the CSV to write ARK info from EZID",
    default="output.csv",
)
def create_arks(input_csv, output_csv):
    generator = EZIDARKHandler()
    results = generator.create_batch_from_csv(
        input_csv, output_csv
    )
    print(f"Processed {len(results)} records")


@cli.command(
    "get_ark", help="Get metadata about an ARK"
)
@click.option(
    "--ark",
    "-a",
    help="The ARK as ark:/99999/fk4cz3dh0"
)
def get_ark(ark):
    handler = EZIDARKHandler()
    handler.get_ark(ark)

@cli.command(
    "switch_statuses", help="Switch status for all items in a CSV"
)
@click.option(
    "--status",
    "-s",
    help="The status to switch to: public, reserved, unavailable",
    default="public"
)
@click.option(
    "--input_csv",
    "-i",
    help="The path to the CSV including ARK metadata",
)
def switch_statuses(status, input_csv):
    handler = EZIDARKHandler()
    handler.batch_switch_status(input_csv, status)


@cli.command(
    "generate_crossref_deposit",
    help="Generate Crossref XML deposit file from CSV metadata"
)
@click.option(
    "--input_csv",
    "-i",
    required=True,
    help="Path to CSV file with metadata (Title, Contributor, Acceptance date, DOI, Resource)",
)
@click.option(
    "--output_xml",
    "-o",
    help="Path for output XML file (default: crossref-deposit-{type}-{timestamp}.xml)",
)
@click.option(
    "--content_type",
    "-t",
    type=click.Choice(['pending_publication', 'report'], case_sensitive=False),
    required=True,
    help="Type of content: pending_publication or report",
)
@click.option(
    "--depositor_name",
    default="TAMU Libraries",
    help="Depositor organization name",
)
@click.option(
    "--depositor_email",
    default="depositor@library.tamu.edu",
    help="Depositor contact email",
)
@click.option(
    "--registrant",
    default="Texas A&M University",
    help="Registrant organization name",
)
def generate_crossref_deposit(input_csv, output_xml, content_type,
                              depositor_name, depositor_email, registrant):
    """Generate Crossref XML deposit file from CSV metadata."""
    handler = CrossrefDepositHandler(
        depositor_name=depositor_name,
        depositor_email=depositor_email,
        registrant=registrant
    )

    result_file = handler.create_batch_from_csv(
        input_csv,
        output_xml,
        content_type
    )

    print(f"Generated Crossref deposit XML: {result_file}")
    print(f"Processed {len(handler.completed)} records")