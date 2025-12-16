import csv
import os
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement
from .templates import PendingPublicationTemplate, ReportTemplate


class CrossrefDepositHandler:
    """Handler for generating Crossref XML deposit files.

    Supports two content types:
    - pending_publication: For preprints/articles accepted but not yet published
    - report: For technical reports and working papers
    """

    def __init__(self,
                 depositor_name=None,
                 depositor_email=None,
                 registrant=None):
        """Initialize with depositor credentials.

        Args:
            depositor_name (str): Name of depositor organization
            depositor_email (str): Contact email for depositor
            registrant (str): Name of registrant organization
        """
        # Use environment variables with fallback to defaults
        self.depositor_name = depositor_name or os.getenv('CROSSREF_DEPOSITOR_NAME', 'TAMU Libraries')
        self.depositor_email = depositor_email or os.getenv('CROSSREF_DEPOSITOR_EMAIL', 'depositor@library.tamu.edu')
        self.registrant = registrant or os.getenv('CROSSREF_REGISTRANT', 'Texas A&M University')
        self.completed = []

    def process_csv(self, input_file):
        """Process CSV file and build metadata list.

        Args:
            input_file (str): Path to CSV file

        Returns:
            list[dict]: List of metadata dictionaries
        """
        metadata_list = []

        with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            # Validate required columns
            required_columns = ['Title', 'Contributor', 'Acceptance date', 'DOI', 'Resource']
            if not all(col in reader.fieldnames for col in required_columns):
                missing = [col for col in required_columns if col not in reader.fieldnames]
                raise ValueError(f"CSV missing required columns: {', '.join(missing)}")

            for row in reader:
                # Normalize column names (case-insensitive matching)
                metadata = {
                    'title': row.get('Title', '').strip(),
                    'contributor': row.get('Contributor', '').strip(),
                    'acceptance_date': row.get('Acceptance date', '').strip(),
                    'doi': row.get('DOI', '').strip(),
                    'resource': row.get('Resource', '').strip(),
                }

                # Skip empty rows
                if not any(metadata.values()):
                    continue

                # Validate required fields
                if not metadata['title']:
                    raise ValueError(f"Missing Title in row: {row}")
                if not metadata['doi']:
                    raise ValueError(f"Missing DOI in row: {row}")
                if not metadata['resource']:
                    raise ValueError(f"Missing Resource in row: {row}")

                metadata_list.append(metadata)
                self.completed.append(metadata)

        return metadata_list

    def generate_deposit_xml(self, content_type, metadata_list):
        """Generate Crossref XML deposit file.

        Args:
            content_type (str): Either 'pending_publication' or 'report'
            metadata_list (list[dict]): List of metadata dictionaries

        Returns:
            str: Complete XML deposit document
        """
        # Generate batch ID with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        batch_id = f"TAMU-{content_type.upper().replace('_', '-')}-{timestamp}"

        # Create template based on content type
        if content_type == 'pending_publication':
            template = PendingPublicationTemplate()
        elif content_type == 'report':
            template = ReportTemplate()
        else:
            raise ValueError(f"Invalid content_type: {content_type}. Must be 'pending_publication' or 'report'")

        # Create root element with head
        root = template.create_doi_batch(
            self.depositor_name,
            self.depositor_email,
            self.registrant,
            batch_id
        )

        # Add body
        body = SubElement(root, 'body')

        # Add content items
        for metadata in metadata_list:
            if content_type == 'pending_publication':
                template.create_pending_publication(body, metadata)
            elif content_type == 'report':
                template.create_report_paper(body, metadata)

        # Format and return XML
        return template.prettify_xml(root)

    def save_xml(self, xml_content, output_file):
        """Save XML content to file.

        Args:
            xml_content (str): XML string to save
            output_file (str): Output file path
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)

    def create_batch_from_csv(self, input_file, output_file, content_type):
        """Main method to process CSV and generate XML deposit file.

        Args:
            input_file (str): Input CSV path
            output_file (str): Output XML path (if None, generates default name)
            content_type (str): Either 'pending_publication' or 'report'

        Returns:
            str: Path to generated XML file
        """
        # Generate default output filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"crossref-deposit-{content_type}-{timestamp}.xml"

        # Process CSV
        metadata_list = self.process_csv(input_file)

        # Generate XML
        xml_content = self.generate_deposit_xml(content_type, metadata_list)

        # Save to file
        self.save_xml(xml_content, output_file)

        return output_file
