# Rozmiary typów TIFF w bajtach na jedną wartość.
# (Typy 6, 8, 11, 12 są dopuszczalne przez standard, ale rzadko występują
# w EXIF-ie — pomijamy je na razie.)
TIFF_TYPE_SIZES = {
    1: 1,   # BYTE
    2: 1,   # ASCII
    3: 2,   # SHORT (uint16)
    4: 4,   # LONG (uint32)
    5: 8,   # RATIONAL (2 x uint32: licznik/mianownik)
    7: 1,   # UNDEFINED (surowe bajty)
    9: 4,   # SLONG
    10: 8,  # SRATIONAL
}

# Najpopularniejsze tagi z IFD0 oraz pod-IFD "Exif".
EXIF_TAGS = {
    0x010F: "Make",
    0x0110: "Model",
    0x0112: "Orientation",
    0x0131: "Software",
    0x0132: "DateTime",
    0x013B: "Artist",
    0x8298: "Copyright",
    0x8769: "ExifIFDPointer",
    0x8825: "GPSInfoIFDPointer",
    0x829A: "ExposureTime",
    0x829D: "FNumber",
    0x8827: "ISOSpeedRatings",
    0x9000: "ExifVersion",
    0x9003: "DateTimeOriginal",
    0x9004: "DateTimeDigitized",
    0x920A: "FocalLength",
}

# Tagi pod-IFD GPS.
GPS_TAGS = {
    0x0001: "GPSLatitudeRef",
    0x0002: "GPSLatitude",
    0x0003: "GPSLongitudeRef",
    0x0004: "GPSLongitude",
    0x0005: "GPSAltitudeRef",
    0x0006: "GPSAltitude",
}


def parse_value(value_bytes, tiff_type, count, endian):
    if tiff_type == 1 or tiff_type == 7:  # BYTE lub UNDEFINED
        return value_bytes.rstrip(b'\x00').decode('latin-1', errors='replace')
    if tiff_type == 2:  # ASCII
        return value_bytes.rstrip(b'\x00').decode('latin-1')
    if tiff_type in (3, 4, 9):  # SHORT / LONG / SLONG
        size = TIFF_TYPE_SIZES[tiff_type]
        signed = (tiff_type == 9)
        values = [int.from_bytes(value_bytes[i*size:(i+1)*size], endian, signed=signed)
                  for i in range(count)]
        return values[0] if count == 1 else values
    if tiff_type in (5, 10):  # RATIONAL / SRATIONAL
        signed = (tiff_type == 10)
        rationals = []
        for i in range(count):
            num = int.from_bytes(value_bytes[i*8:i*8+4], endian, signed=signed)
            den = int.from_bytes(value_bytes[i*8+4:i*8+8], endian, signed=signed)
            rationals.append(f"{num}/{den}" if den != 1 else str(num))
        return rationals[0] if count == 1 else rationals
    return f"<typ {tiff_type}, {count} wartości>"


def decode_entry(data, offset, endian):
    tag = int.from_bytes(data[offset:offset+2], endian)
    tiff_type = int.from_bytes(data[offset+2:offset+4], endian)
    count = int.from_bytes(data[offset+4:offset+8], endian)
    value_field = data[offset+8:offset+12]

    type_size = TIFF_TYPE_SIZES.get(tiff_type, 0)
    if type_size == 0:
        return tag, f"<typ {tiff_type} nieznany>"

    total_size = type_size * count

    # Jeśli dane mieszczą się w 4 bajtach, są tu bezpośrednio.
    # Inaczej — te 4 bajty to offset do miejsca w TIFF, gdzie leżą dane.
    if total_size <= 4:
        value_bytes = value_field[:total_size]
    else:
        data_offset = int.from_bytes(value_field, endian)
        value_bytes = data[data_offset:data_offset + total_size]

    return tag, parse_value(value_bytes, tiff_type, count, endian)


def decode_ifd(data, offset, endian, name, tag_names):
    num_entries = int.from_bytes(data[offset:offset+2], endian)
    print(f"  {name} ({num_entries} wpisów):")

    entries = []
    for i in range(num_entries):
        entry_offset = offset + 2 + i * 12
        tag, value = decode_entry(data, entry_offset, endian)
        tag_name = tag_names.get(tag, f"0x{tag:04X}")
        print(f"    {tag_name}: {value!r}")
        entries.append((tag, value))

    # Rekurencja: jeśli wpis wskazuje na pod-IFD, schodzimy w niego.
    for tag, value in entries:
        if tag == 0x8769:
            decode_ifd(data, value, endian, "  Exif sub-IFD", EXIF_TAGS)
        elif tag == 0x8825:
            decode_ifd(data, value, endian, "  GPS sub-IFD", GPS_TAGS)


def decode_exif(data: bytes) -> None:
    bom = data[:2]
    if bom == b'II':
        endian = 'little'
    elif bom == b'MM':
        endian = 'big'
    else:
        print(f"  Nieznany byte order: {bom!r}")
        return

    magic = int.from_bytes(data[2:4], endian)
    if magic != 0x002A:
        print(f"  Zły TIFF magic: {magic:#06x}")
        return

    ifd0_offset = int.from_bytes(data[4:8], endian)
    print(f"  Byte order: {endian}-endian, IFD0 @ offset {ifd0_offset}")
    decode_ifd(data, ifd0_offset, endian, "IFD0", EXIF_TAGS)
