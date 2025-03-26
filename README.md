import binascii

# FSPEC Mapping with Data Lengths
FSPEC_MAPPING = {
    1: ("Data Source Identification", 2),       
    2: ("Track Number", 2),                     
    3: ("Time of Applicability for Position", 3), 
    4: ("Position in WGS-84 (High Resolution)", 8), 
    5: ("Time of Applicability for Velocity", 3), 
    6: ("Target Address", 3),                    
    7: ("Time of Message Reception of Position", 3), 
    8: ("Geometric Height", 2),                   
    9: ("Flight Level", 2),                       
    10: ("Magnetic Heading", 2),                  
    11: ("Barometric Vertical Rate", 2),          
    12: ("Geometric Vertical Rate", 2),           
    13: ("Message Amplitude", 1),                 
}

# LSB Multipliers for Specific Data Items
LSB_VALUES = {
    "Time of Applicability for Position": 1 / 128,
    "Position in WGS-84 (High Resolution)": 180 / (2**30),  # Applied to both Latitude & Longitude
    "Time of Applicability for Velocity": 1 / 128,
    "Target Address": 1,  # No conversion needed
    "Time of Message Reception of Position": 1 / 128,
    "Geometric Height": 6.25,
    "Flight Level": 1 / 4,
    "Magnetic Heading": 360 / (2**16),
    "Barometric Vertical Rate": 6.25,
    "Geometric Vertical Rate": 6.25,
    "Message Amplitude": 81,
}

def parse_fspec_and_data(hex_packet):
    """ Extract CAT, Length, FSPEC and Data Items from a CAT21 ASTERIX packet """
    
    try:
        # Convert hex string to bytes
        packet_bytes = bytes.fromhex(hex_packet)
        print(f"Raw Packet Bytes: {packet_bytes.hex().upper()}")

        # Extract Category and Length
        if len(packet_bytes) < 3:
            print("Error: Packet too short to contain CAT and Length.")
            return {}

        category = packet_bytes[0]
        length = int.from_bytes(packet_bytes[1:3], byteorder='big')

        print(f"Category: {category}")
        print(f"Packet Length: {length}")

        # Extract FSPEC bytes (starting after CAT and LEN)
        fspec_bytes = []
        index = 3  # FSPEC starts at byte 3 (after CAT and LEN)

        while index < len(packet_bytes):
            fspec_byte = packet_bytes[index]
            fspec_bytes.append(fspec_byte)
            index += 1
            if (fspec_byte & 0x80) == 0:  # If MSB is 0, FSPEC ends
                break

        if not fspec_bytes:
            print("Error: No FSPEC bytes found.")
            return {}

        # Convert FSPEC bytes to binary string
        fspec_bits = "".join(f"{byte:08b}" for byte in fspec_bytes)
        print(f"FSPEC Bytes: {[hex(b) for b in fspec_bytes]}")
        print(f"FSPEC Bits: {fspec_bits}")

        # Extract Data Items based on FSPEC bits
        data_items = {}
        data_start_index = index  # Start extracting data from this byte

        for i, bit in enumerate(fspec_bits, start=1):
            if bit == "1":  # If the bit is set, extract the corresponding data item
                item_info = FSPEC_MAPPING.get(i)

                if item_info:
                    item_name, data_length = item_info
                else:
                    item_name, data_length = f"Unknown Data Item {i}", 2

                if data_start_index + data_length <= len(packet_bytes):
                    raw_hex = packet_bytes[data_start_index:data_start_index + data_length].hex().upper()
                    raw_value = int.from_bytes(packet_bytes[data_start_index:data_start_index + data_length], byteorder='big')
                    data_start_index += data_length  # Move to next data item

                    print(f"\nItem: {item_name}")
                    print(f"Hex Value: {raw_hex}")
                    print(f"Raw Decimal: {raw_value}")
                    
                    # Apply LSB scaling if needed
                    if item_name in LSB_VALUES:
                        scaled_value = raw_value * LSB_VALUES[item_name]
                        data_items[item_name] = round(scaled_value, 6)
                        print(f"Scaled Value: {data_items[item_name]}")
                    else:
                        data_items[item_name] = raw_value  # Keep original decimal value
                        print("No Scaling Applied")

        return data_items

    except ValueError as e:
        print(f"Error: {e}")
        return {}

# Example Hex Packet (Replace with actual ADS-B CAT21 hex packet)
hex_packet = "14130001551B79048EDDDD1B3EA9EE551B7906A0F5551B7917C005F074920000000051"

data_items = parse_fspec_and_data(hex_packet)

# Print extracted Data Items in Decimal with Scaling Applied
print("\nExtracted Data Items (Decimal Values with LSB Scaling):")
for key, value in data_items.items():
    print(f"{key}: {value}")
