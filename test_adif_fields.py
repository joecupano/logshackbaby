#!/usr/bin/env python3
"""
Test script to verify ADIF parser correctly processes all fields
"""

import sys
sys.path.insert(0, 'backend')

from adif_parser import ADIFParser

# Test ADIF content with multiple fields including additional ones
test_adif = """
<ADIF_VER:5>3.1.6
<PROGRAMID:12>LogShackBaby
<EOH>

<CALL:5>W1ABC <QSO_DATE:8>20240101 <TIME_ON:6>143000 
<BAND:3>20m <MODE:3>SSB <FREQ:8>14.250000 
<RST_SENT:2>59 <RST_RCVD:2>59 
<STATION_CALLSIGN:5>K1XYZ <MY_GRIDSQUARE:6>FN42aa <GRIDSQUARE:6>FN31pr
<NAME:4>John <QTH:6>Boston <COMMENT:13>Great signal!
<TX_PWR:3>100 <OPERATOR:5>K2DEF <CONTEST_ID:7>CQ-WPX
<QSL_SENT:1>Y <LOTW_QSLSDATE:8>20240115 <EQSL_QSL_SENT:1>Y
<MY_COUNTRY:3>USA <COUNTRY:3>USA <DXCC:3>291
<MY_ANTENNA:13>dipole 40ft <ANT_AZ:3>045 <ANT_EL:2>15
<PROP_MODE:2>F2 <SRX:3>123 <STX:3>456
<EOR>

<CALL:5>K4DEF <QSO_DATE:8>20240101 <TIME_ON:6>150000 
<BAND:3>40m <MODE:2>CW <FREQ:7>7.025000 
<RST_SENT:3>599 <RST_RCVD:3>579 
<STATION_CALLSIGN:5>K1XYZ
<EOR>
"""

def test_parser():
    print("Testing ADIF Parser - All Fields Processing")
    print("=" * 60)
    
    parser = ADIFParser()
    records = parser.parse_file(test_adif)
    
    print(f"\n✓ Parsed {len(records)} records\n")
    
    # Test first record (with many additional fields)
    record1 = records[0]
    print("Record 1: W1ABC")
    print("-" * 60)
    print("Core fields:")
    for field in ['call', 'qso_date', 'time_on', 'band', 'mode', 'rst_sent', 'rst_rcvd']:
        if field in record1:
            print(f"  {field:20s} = {record1[field]}")
    
    print("\nAdditional fields:")
    if 'additional_fields' in record1:
        for field, value in record1['additional_fields'].items():
            print(f"  {field:20s} = {value}")
        print(f"\n✓ Captured {len(record1['additional_fields'])} additional fields")
    else:
        print("  (none)")
    
    # Test second record (minimal fields)
    print("\n" + "=" * 60)
    record2 = records[1]
    print("Record 2: K4DEF")
    print("-" * 60)
    print("Core fields:")
    for field in ['call', 'qso_date', 'time_on', 'band', 'mode', 'rst_sent', 'rst_rcvd']:
        if field in record2:
            print(f"  {field:20s} = {record2[field]}")
    
    print("\nAdditional fields:")
    if 'additional_fields' in record2:
        print(f"  {len(record2['additional_fields'])} fields")
    else:
        print("  (none)")
    
    # Verify specific fields
    print("\n" + "=" * 60)
    print("Verification Tests:")
    print("-" * 60)
    
    tests = [
        ("Core field 'call' present", 'call' in record1, True),
        ("Core field 'band' present", 'band' in record1, True),
        ("Additional fields exist", 'additional_fields' in record1, True),
        ("TX_PWR in additional", 'tx_pwr' in record1.get('additional_fields', {}), True),
        ("OPERATOR in additional", 'operator' in record1.get('additional_fields', {}), True),
        ("CONTEST_ID in additional", 'contest_id' in record1.get('additional_fields', {}), True),
        ("QSL_SENT in additional", 'qsl_sent' in record1.get('additional_fields', {}), True),
        ("MY_ANTENNA in additional", 'my_antenna' in record1.get('additional_fields', {}), True),
        ("PROP_MODE in additional", 'prop_mode' in record1.get('additional_fields', {}), True),
    ]
    
    all_passed = True
    for test_name, result, expected in tests:
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"{status:8s} {test_name}")
        if result != expected:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests PASSED - ADIF parser correctly processes all fields!")
    else:
        print("✗ Some tests FAILED - Please review the parser implementation")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = test_parser()
    sys.exit(0 if success else 1)
