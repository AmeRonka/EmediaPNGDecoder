import sys
from pathlib import Path

from png_reader import read_chunk, verify_signature
from decoders import DECODERS
from anonymize import anonymize


def parse(path: str) -> None:
    data = Path(path).read_bytes()
    print(f"Plik: {path} ({len(data)} B)")

    if not verify_signature(data):
        print("To nie jest plik PNG!")
        sys.exit(1)
    print("Sygnatura PNG — OK\n")

    offset = 8
    while offset < len(data):
        chunk_type, chunk_data, crc_ok, next_offset = read_chunk(data, offset)
        crc_status = "OK" if crc_ok else "BŁĄD!"
        print(f"[{offset:#08x}] {chunk_type:4s}  length={len(chunk_data):>6}  CRC={crc_status}")

        decoder = DECODERS.get(chunk_type)
        if decoder is not None:
            decoder(chunk_data)

        offset = next_offset
        if chunk_type == "IEND":
            break


if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == "anonymize":
        anonymize(sys.argv[2], sys.argv[3])
    else:
        path = sys.argv[1] if len(sys.argv) > 1 else 'Example.png'
        parse(path)
