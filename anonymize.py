from pathlib import Path

from png_reader import PNG_SIGNATURE, read_chunk, verify_signature

# Tylko te cztery typy chunków są standardowymi critical chunks w PNG.
# Wszystko inne (w tym nieznane critical chunks) traktujemy jako potencjalny
# nośnik ukrytej informacji i wyrzucamy przy anonimizacji.
CRITICAL_ALLOWED = {"IHDR", "PLTE", "IDAT", "IEND"}


def anonymize(input_path: str, output_path: str) -> None:
    data = Path(input_path).read_bytes()

    if not verify_signature(data):
        print("To nie jest plik PNG!")
        return

    output = bytearray(PNG_SIGNATURE)
    offset = 8
    removed = []

    while offset < len(data):
        chunk_type, chunk_data, _, next_offset = read_chunk(data, offset)

        if chunk_type in CRITICAL_ALLOWED:
            # kopiujemy cały chunk (length + type + data + CRC) bez zmian
            output.extend(data[offset:next_offset])
        else:
            removed.append((chunk_type, len(chunk_data)))

        offset = next_offset
        if chunk_type == "IEND":
            break

    trailing = len(data) - offset
    if trailing > 0:
        print(f"Pominięto {trailing} B śmieci za IEND")

    Path(output_path).write_bytes(output)

    print(f"Zapisano {output_path}")
    print(f"Rozmiar: {len(data)} B -> {len(output)} B "
          f"(usunięto {len(data) - len(output)} B)")
    if removed:
        print("Usunięte chunki:")
        for name, length in removed:
            print(f"  {name}: {length} B")
    else:
        print("Nie było chunków do usunięcia.")
