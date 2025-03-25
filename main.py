def parse_fspec_and_data(hex_packet):
    """ Extract CAT, Length, FSPEC and Data Items from a CAT21 ASTERIX packet """

    try:
        # Convert hex string to bytes
        packet_bytes = bytes.fromhex(hex_packet)
        print(f"Raw Packet Bytes: {packet_bytes.hex().upper()}")  # Debugging print

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
                    raw_value = int.from_bytes(packet_bytes[data_start_index:data_start_index + data_length],
                                               byteorder='big')
                    data_start_index += data_length  # Move to next data item

                    # Apply LSB scaling if needed
                    if item_name in LSB_VALUES:
                        scaled_value = raw_value * LSB_VALUES[item_name]
                        data_items[item_name] = round(scaled_value, 6)
                    else:
                        data_items[item_name] = raw_value  # Keep original decimal value
                else:
                    print(f"Error: Insufficient data for {item_name}.")

        return data_items

    except ValueError as e:
        print(f"Error: {e}")
        return {}

