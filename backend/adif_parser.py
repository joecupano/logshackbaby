"""
ADIF (Amateur Data Interchange Format) Parser
Supports ADIF 3.1.6 specification
Parses ADIF files for amateur radio QSO logs
"""
import re
import hashlib
from datetime import datetime


class ADIFParser:
    """Parse ADIF 3.1.6 format amateur radio log files"""
    
    # ADIF version supported
    ADIF_VERSION = "3.1.6"
    
    # Core fields we extract to dedicated columns (limited set for indexing)
    CORE_FIELDS = {
        'qso_date', 'time_on', 'call', 'band', 'mode', 'freq',
        'rst_sent', 'rst_rcvd', 'qso_date_off', 'time_off',
        'station_callsign', 'my_gridsquare', 'gridsquare',
        'name', 'qth', 'comment'
    }
    
    # Comprehensive list of all ADIF 3.1.6 fields
    # All fields not in CORE_FIELDS will be stored in additional_fields JSON
    ALL_ADIF_FIELDS = {
        # QSO details
        'qso_date', 'time_on', 'qso_date_off', 'time_off', 'call', 'band', 'band_rx',
        'freq', 'freq_rx', 'mode', 'submode', 'rst_sent', 'rst_rcvd',
        
        # Station information
        'station_callsign', 'operator', 'owner_callsign', 'my_name', 'my_city',
        'my_cnty', 'my_country', 'my_cq_zone', 'my_dxcc', 'my_fists', 'my_gridsquare',
        'my_iota', 'my_iota_island_id', 'my_itu_zone', 'my_lat', 'my_lon', 'my_postal_code',
        'my_rig', 'my_sig', 'my_sig_info', 'my_sota_ref', 'my_state', 'my_street',
        'my_usaca_counties', 'my_vucc_grids', 'my_antenna', 'my_antenna_intl',
        'my_arrl_sect', 'my_wwff_ref', 'my_pota_ref',
        
        # Contacted station information
        'name', 'qth', 'gridsquare', 'lat', 'lon', 'country', 'cnty', 'cont', 'cqz',
        'dxcc', 'email', 'eq_call', 'fists', 'fists_cc', 'iota', 'iota_island_id',
        'ituz', 'pfx', 'qslmsg', 'region', 'rig', 'rig_intl', 'rx_pwr', 'sig',
        'sig_info', 'silent_key', 'skcc', 'sota_ref', 'state', 'ten_ten', 'uksmg',
        'usaca_counties', 've_prov', 'vucc_grids', 'web', 'age', 'address',
        'address_intl', 'arrl_sect', 'wwff_ref', 'pota_ref', 'hamlogeu_qso_upload_date',
        'hamqth_qso_upload_date', 'hrdlog_qso_upload_date', 'qrzcom_qso_upload_date',
        
        # Award tracking
        'award_submitted', 'award_granted', 'credit_submitted', 'credit_granted',
        
        # Power and propagation
        'tx_pwr', 'rx_pwr', 'prop_mode', 'sat_mode', 'sat_name', 'ant_az', 'ant_el',
        'ant_path', 'a_index', 'k_index', 'sfi', 'max_bursts', 'ms_shower',
        'nr_bursts', 'nr_pings', 'force_init', 'public_key',
        
        # Contest information
        'contest_id', 'srx', 'srx_string', 'stx', 'stx_string', 'precedence',
        'check', 'class', 'arrl_sect', 'cnty',
        
        # QSL information
        'qsl_sent', 'qsl_sent_via', 'qsl_rcvd', 'qsl_rcvd_via', 'qslrdate',
        'qslsdate', 'lotw_qsl_sent', 'lotw_qsl_rcvd', 'lotw_qslsdate', 'lotw_qslrdate',
        'eqsl_qsl_sent', 'eqsl_qsl_rcvd', 'eqsl_qslsdate', 'eqsl_qslrdate',
        'clublog_qso_upload_date', 'clublog_qso_upload_status',
        
        # Digital modes
        'app_defined', 'darc_dok', 'distance', 'notes', 'qso_complete', 'qso_random',
        'swl', 'ten_ten', 'uksmg',
        
        # Other
        'comment', 'intl_comment', 'guest_op', 'qth_intl', 'name_intl',
        'rig_intl', 'address_intl', 'my_antenna_intl', 'notes_intl',
        'app_n1mm_contacttype', 'app_n1mm_radio', 'app_n1mm_run1run2',
        'app_n1mm_radiointerfaced', 'app_n1mm_isoriginal', 'app_n1mm_netbiosname',
        'app_n1mm_isrunqso', 'app_eqsl_ag', 'app_lotw_2xqsl', 'app_lotw_credit_granted',
        'app_lotw_npsunit', 'app_lotw_owncall', 'app_lotw_qslmode', 'app_lotw_rxqsl',
        'app_lotw_rxqso'
    }
    
    # ADIF 3.1.6 enumeration fields for validation
    BAND_VALUES = {
        '2190m', '630m', '560m', '160m', '80m', '60m', '40m', '30m', '20m',
        '17m', '15m', '12m', '10m', '8m', '6m', '5m', '4m', '2m', '1.25m',
        '70cm', '33cm', '23cm', '13cm', '9cm', '6cm', '3cm', '1.25cm', '6mm',
        '4mm', '2.5mm', '2mm', '1mm', 'submm'
    }
    
    MODE_VALUES = {
        'AM', 'ARDOP', 'ATV', 'C4FM', 'CHIP', 'CLO', 'CONTESTI', 'CW', 'DIGITALVOICE',
        'DOMINO', 'DSTAR', 'FAX', 'FM', 'FSK441', 'FT8', 'FT4', 'HELL', 'ISCAT',
        'JT4', 'JT6M', 'JT9', 'JT44', 'JT65', 'MFSK', 'MSK144', 'MT63', 'OLIVIA',
        'OPERA', 'PAC', 'PAX', 'PKT', 'PSK', 'PSK2K', 'Q15', 'QRA64', 'ROS',
        'RTTY', 'RTTYM', 'SSB', 'SSTV', 'T10', 'THOR', 'THRB', 'TOR', 'V4',
        'VOI', 'WINMOR', 'WSPR', 'JS8'
    }
    
    def __init__(self):
        self.records = []
        self.header = {}
        
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
        
        # Parse header
        header_end = file_content.lower().find('<eoh>')
        if header_end != -1:
            self.parse_header(file_content[:header_end])
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
    
    def parse_header(self, header_text):
        """
        Parse ADIF header section
        
        Args:
            header_text: String containing header section
        """
        pattern = r'<([^:>]+):(\d+)(?::([^>]+))?>([^<]*)'
        matches = re.findall(pattern, header_text, re.IGNORECASE)
        
        for field_name, length, data_type, value in matches:
            field_name = field_name.lower().strip()
            length = int(length)
            value = value[:length].strip()
            self.header[field_name] = value
    
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
            
            # Skip empty values
            if not value:
                continue
            
            # Normalize certain fields
            if field_name == 'band' or field_name == 'band_rx':
                value = self.normalize_band(value)
            elif field_name == 'mode' or field_name == 'submode':
                value = self.normalize_mode(value)
            
            # Store in appropriate location
            if field_name in self.CORE_FIELDS:
                record[field_name] = value
            else:
                # All other fields go to additional_fields
                # This captures ALL ADIF fields not in core set
                additional_fields[field_name] = value
        
        # Always include additional_fields even if empty for consistency
        if additional_fields:
            record['additional_fields'] = additional_fields
        
        # Generate hash for deduplication
        if record:
            record['qso_hash'] = self.generate_qso_hash(record)
        
        return record
    
    def normalize_band(self, band):
        """Normalize band value to ADIF 3.1.6 standard"""
        band = band.upper().strip()
        # Convert common variations
        if band == '20M' or band == '20':
            return '20m'
        if band == '40M' or band == '40':
            return '40m'
        if band == '80M' or band == '80':
            return '80m'
        if band == '2M' or band == '2':
            return '2m'
        if band == '70CM' or band == '70':
            return '70cm'
        # Return as lowercase for consistency
        return band.lower()
    
    def normalize_mode(self, mode):
        """Normalize mode value to ADIF 3.1.6 standard"""
        mode = mode.upper().strip()
        # Handle common variations
        if mode in ['USB', 'LSB']:
            return 'SSB'
        return mode
    
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
