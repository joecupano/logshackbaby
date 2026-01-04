"""
ADIF (Amateur Data Interchange Format) Parser
Supports parsing ADIF files for amateur radio QSO logs
"""
import re
import hashlib
from datetime import datetime


class ADIFParser:
    """Parse ADIF format amateur radio log files"""
    
    # Core fields we extract to dedicated columns
    CORE_FIELDS = {
        'qso_date', 'time_on', 'call', 'band', 'mode', 'freq',
        'rst_sent', 'rst_rcvd', 'qso_date_off', 'time_off',
        'station_callsign', 'my_gridsquare', 'gridsquare',
        'name', 'qth', 'comment'
    }
    
    def __init__(self):
        self.records = []
        
    def parse_file(self, file_content):
        """
        Parse ADIF file content
        
        Args:
            file_content: String content of ADIF file
            
        Returns:
            List of parsed QSO records
        """
        # Convert bytes to string if needed
        if isinstance(file_content, bytes):
            file_content = file_content.decode('utf-8', errors='ignore')
        
        # Find header end marker
        header_end = file_content.lower().find('<eoh>')
        if header_end != -1:
            file_content = file_content[header_end + 5:]
        
        # Split into records by <eor> marker
        records_raw = re.split(r'<eor>', file_content, flags=re.IGNORECASE)
        
        self.records = []
        for record_raw in records_raw:
            if not record_raw.strip():
                continue
                
            record = self.parse_record(record_raw)
            if record and self.validate_record(record):
                self.records.append(record)
        
        return self.records
    
    def parse_record(self, record_text):
        """
        Parse a single ADIF record
        
        Args:
            record_text: String containing one QSO record
            
        Returns:
            Dictionary of field:value pairs
        """
        # Pattern to match ADIF fields: <field:length[:type]>data
        pattern = r'<([^:>]+):(\d+)(?::([^>]+))?>([^<]*)'
        matches = re.findall(pattern, record_text, re.IGNORECASE)
        
        record = {}
        additional_fields = {}
        
        for field_name, length, data_type, value in matches:
            field_name = field_name.lower().strip()
            length = int(length)
            value = value[:length].strip()
            
            if not value:
                continue
            
            # Store in appropriate location
            if field_name in self.CORE_FIELDS:
                record[field_name] = value
            else:
                additional_fields[field_name] = value
        
        if additional_fields:
            record['additional_fields'] = additional_fields
        
        # Generate hash for deduplication
        if record:
            record['qso_hash'] = self.generate_qso_hash(record)
        
        return record
    
    def validate_record(self, record):
        """
        Validate that record has minimum required fields
        
        Args:
            record: Dictionary of QSO data
            
        Returns:
            Boolean indicating if record is valid
        """
        required_fields = ['qso_date', 'time_on', 'call']
        return all(field in record for field in required_fields)
    
    def generate_qso_hash(self, record):
        """
        Generate unique hash for QSO to enable deduplication
        Uses: callsign, date, time, band/freq, mode
        
        Args:
            record: Dictionary of QSO data
            
        Returns:
            SHA256 hash string
        """
        # Create normalized string for hashing
        hash_components = [
            record.get('call', '').upper(),
            record.get('qso_date', ''),
            record.get('time_on', ''),
            record.get('band', record.get('freq', '')),
            record.get('mode', ''),
            record.get('station_callsign', '').upper()
        ]
        
        hash_string = '|'.join(hash_components)
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def get_statistics(self):
        """
        Get statistics about parsed records
        
        Returns:
            Dictionary with statistics
        """
        if not self.records:
            return {
                'total': 0,
                'bands': {},
                'modes': {},
                'date_range': None
            }
        
        bands = {}
        modes = {}
        dates = []
        
        for record in self.records:
            # Count bands
            band = record.get('band', 'Unknown')
            bands[band] = bands.get(band, 0) + 1
            
            # Count modes
            mode = record.get('mode', 'Unknown')
            modes[mode] = modes.get(mode, 0) + 1
            
            # Collect dates
            if 'qso_date' in record:
                dates.append(record['qso_date'])
        
        date_range = None
        if dates:
            dates.sort()
            date_range = {
                'earliest': dates[0],
                'latest': dates[-1]
            }
        
        return {
            'total': len(self.records),
            'bands': bands,
            'modes': modes,
            'date_range': date_range
        }
