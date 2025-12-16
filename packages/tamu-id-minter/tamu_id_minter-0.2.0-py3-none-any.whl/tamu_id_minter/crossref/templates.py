from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from datetime import datetime


class CrossrefXMLTemplate:
    """Base class for Crossref XML generation."""

    NAMESPACE = "http://www.crossref.org/schema/5.4.0"
    XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
    SCHEMA_LOCATION = "http://www.crossref.org/schema/5.4.0 http://www.crossref.org/schemas/crossref5.4.0.xsd"

    def create_doi_batch(self, depositor_name, depositor_email, registrant, batch_id):
        """Create root doi_batch element with proper namespaces.

        Args:
            depositor_name (str): Name of depositor organization
            depositor_email (str): Contact email for depositor
            registrant (str): Name of registrant organization
            batch_id (str): Unique batch identifier

        Returns:
            Element: Root doi_batch element with head section
        """
        root = Element('doi_batch', {
            'version': '5.4.0',
            'xmlns': self.NAMESPACE,
            'xmlns:xsi': self.XSI_NAMESPACE,
            'xsi:schemaLocation': self.SCHEMA_LOCATION
        })

        self.add_head(root, depositor_name, depositor_email, registrant, batch_id)
        return root

    def add_head(self, root, depositor_name, depositor_email, registrant, batch_id):
        """Add head section with depositor info and timestamp.

        Args:
            root (Element): Root element to add head section to
            depositor_name (str): Name of depositor organization
            depositor_email (str): Contact email for depositor
            registrant (str): Name of registrant organization
            batch_id (str): Unique batch identifier
        """
        head = SubElement(root, 'head')

        # Batch ID
        doi_batch_id = SubElement(head, 'doi_batch_id')
        doi_batch_id.text = batch_id

        # Timestamp
        timestamp = SubElement(head, 'timestamp')
        timestamp.text = datetime.now().strftime("%Y%m%d%H%M%S")

        # Depositor
        depositor = SubElement(head, 'depositor')
        depositor_name_elem = SubElement(depositor, 'depositor_name')
        depositor_name_elem.text = depositor_name
        email_address = SubElement(depositor, 'email_address')
        email_address.text = depositor_email

        # Registrant
        registrant_elem = SubElement(head, 'registrant')
        registrant_elem.text = registrant

    def parse_contributors(self, contributor_string):
        """Parse contributor string into list of (given_name, surname) tuples.

        Supports formats:
        - "Last, First"
        - "First Last"
        - Multiple contributors separated by " and " or " ; "

        Args:
            contributor_string (str): Comma-separated contributor string

        Returns:
            list[tuple]: List of (given_name, surname) tuples
        """
        contributors = []

        # Split on common separators
        if ' and ' in contributor_string:
            parts = contributor_string.split(' and ')
        elif ' ; ' in contributor_string:
            parts = contributor_string.split(' ; ')
        else:
            parts = [contributor_string]

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Check if "Last, First" format
            if ',' in part:
                surname, given_name = part.split(',', 1)
                surname = surname.strip()
                given_name = given_name.strip()
            else:
                # "First Last" format - last word is surname
                name_parts = part.split()
                if len(name_parts) == 1:
                    given_name = ''
                    surname = name_parts[0]
                else:
                    surname = name_parts[-1]
                    given_name = ' '.join(name_parts[:-1])

            contributors.append((given_name, surname))

        return contributors

    def add_contributors(self, parent, contributor_string):
        """Add contributors element with person_name elements.

        Args:
            parent (Element): Parent element to add contributors to
            contributor_string (str): Contributor string to parse
        """
        contributors_elem = SubElement(parent, 'contributors')
        contributors_list = self.parse_contributors(contributor_string)

        for idx, (given_name, surname) in enumerate(contributors_list):
            sequence = "first" if idx == 0 else "additional"
            person_name = SubElement(contributors_elem, 'person_name', {
                'sequence': sequence,
                'contributor_role': 'author'
            })

            if given_name:
                given_name_elem = SubElement(person_name, 'given_name')
                given_name_elem.text = given_name

            surname_elem = SubElement(person_name, 'surname')
            surname_elem.text = surname

    def add_titles(self, parent, title):
        """Add titles element.

        Args:
            parent (Element): Parent element to add titles to
            title (str): Title text
        """
        titles = SubElement(parent, 'titles')
        title_elem = SubElement(titles, 'title')
        title_elem.text = title

    def parse_date(self, date_string):
        """Parse date string into (month, day, year) tuple.

        Supports formats:
        - YYYY-MM-DD (ISO 8601)
        - MM/DD/YYYY
        - DD/MM/YYYY

        Args:
            date_string (str): Date string to parse

        Returns:
            tuple: (month, day, year) as strings
        """
        date_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
        ]

        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_string.strip(), fmt)
                return (str(dt.month), str(dt.day), str(dt.year))
            except ValueError:
                continue

        # If all formats fail, raise error
        raise ValueError(f"Unable to parse date: {date_string}. Expected format: YYYY-MM-DD")

    def add_doi_data(self, parent, doi, resource):
        """Add doi_data element.

        Args:
            parent (Element): Parent element to add doi_data to
            doi (str): DOI identifier
            resource (str): Resource URL
        """
        doi_data = SubElement(parent, 'doi_data')

        doi_elem = SubElement(doi_data, 'doi')
        # Normalize DOI (remove https://doi.org/ prefix if present)
        doi_clean = doi.replace('https://doi.org/', '').replace('http://doi.org/', '').strip()
        doi_elem.text = doi_clean

        resource_elem = SubElement(doi_data, 'resource')
        resource_elem.text = resource

    def prettify_xml(self, elem):
        """Return formatted XML string.

        Args:
            elem (Element): Element to format

        Returns:
            str: Formatted XML string
        """
        rough_string = tostring(elem, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')


class PendingPublicationTemplate(CrossrefXMLTemplate):
    """Template for pending publication XML generation."""

    def create_pending_publication(self, parent, metadata):
        """Create pending_publication element.

        Args:
            parent (Element): Parent XML element (body)
            metadata (dict): Contains title, contributor, acceptance_date, doi, resource
        """
        pending_pub = SubElement(parent, 'pending_publication', {'language': 'en'})

        # Contributors
        self.add_contributors(pending_pub, metadata['contributor'])

        # Titles
        self.add_titles(pending_pub, metadata['title'])

        # Acceptance date
        self.add_acceptance_date(pending_pub, metadata['acceptance_date'])

        # DOI data
        self.add_doi_data(pending_pub, metadata['doi'], metadata['resource'])

    def add_acceptance_date(self, parent, date_string):
        """Add acceptance_date element from date string.

        Args:
            parent (Element): Parent element to add acceptance_date to
            date_string (str): Date string to parse
        """
        month, day, year = self.parse_date(date_string)

        acceptance_date = SubElement(parent, 'acceptance_date')

        month_elem = SubElement(acceptance_date, 'month')
        month_elem.text = month

        day_elem = SubElement(acceptance_date, 'day')
        day_elem.text = day

        year_elem = SubElement(acceptance_date, 'year')
        year_elem.text = year


class ReportTemplate(CrossrefXMLTemplate):
    """Template for report/working paper XML generation."""

    def create_report_paper(self, parent, metadata, publisher='Texas A&M University',
                           institution='Texas A&M University Libraries'):
        """Create report-paper element.

        Args:
            parent (Element): Parent XML element (body)
            metadata (dict): Contains title, contributor, acceptance_date, doi, resource
            publisher (str): Publisher name
            institution (str): Institution name
        """
        report_paper = SubElement(parent, 'report-paper')
        report_metadata = SubElement(report_paper, 'report-paper_metadata', {'language': 'en'})

        # Contributors
        self.add_contributors(report_metadata, metadata['contributor'])

        # Titles
        self.add_titles(report_metadata, metadata['title'])

        # Publication date (use acceptance_date as publication date)
        self.add_publication_date(report_metadata, metadata['acceptance_date'])

        # Publisher
        self.add_publisher(report_metadata, publisher)

        # Institution
        self.add_institution(report_metadata, institution)

        # DOI data
        self.add_doi_data(report_metadata, metadata['doi'], metadata['resource'])

    def add_publication_date(self, parent, date_string):
        """Add publication_date element from date string.

        Args:
            parent (Element): Parent element to add publication_date to
            date_string (str): Date string to parse
        """
        month, day, year = self.parse_date(date_string)

        pub_date = SubElement(parent, 'publication_date', {'media_type': 'online'})

        month_elem = SubElement(pub_date, 'month')
        month_elem.text = month

        day_elem = SubElement(pub_date, 'day')
        day_elem.text = day

        year_elem = SubElement(pub_date, 'year')
        year_elem.text = year

    def add_publisher(self, parent, publisher_name):
        """Add publisher element.

        Args:
            parent (Element): Parent element to add publisher to
            publisher_name (str): Publisher name
        """
        publisher = SubElement(parent, 'publisher')
        publisher_name_elem = SubElement(publisher, 'publisher_name')
        publisher_name_elem.text = publisher_name

    def add_institution(self, parent, institution_name):
        """Add institution element.

        Args:
            parent (Element): Parent element to add institution to
            institution_name (str): Institution name
        """
        institution = SubElement(parent, 'institution')
        institution_name_elem = SubElement(institution, 'institution_name')
        institution_name_elem.text = institution_name
