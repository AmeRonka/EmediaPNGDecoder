import sys
from pathlib import Path

from png_reader import read_chunk, verify_signature
from decoders import DECODERS
from anonymize import anonymize
from fourier import display_image_and_fourier, test_fourier


def print_theory_analysis() -> None:
    print("\n--- Wpływ kompresji i kodowania na ukrywanie danych ---")
    print("1. Metody kompresji:")
    print("   Dedykowane algorytmy bezstratne (jak DEFLATE w PNG) pozwalają ukryć dane w szumie LSB")
    print("   (Least Significant Bit) pikseli lub poprzez manipulację filtrami przed kompresją")
    print("   Algorytmy stratne (np. JPEG) niszczą modyfikacje LSB podczas kwantyzacji,")
    print("   dlatego steganografia w nich wymaga ingerencji w same współczynniki DCT")
    print("\n2. Kodowanie kolorów:")
    print("   W przypadku obrazów paletowych (Indexed Color w PNG), zmiana LSB indeksu")
    print("   może spowodować przeskoczenie na zupełnie inny kolor w palecie, co będzie")
    print("   od razu widoczne gołym okiem. Z kolei w formacie RGB(A) modyfikacja LSB")
    print("   jest niezauważalna dla człowieka, co czyni RGB lepszym nośnikiem do steganografii \n")


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

    print_theory_analysis()
    
    try:
        display_image_and_fourier(path)
    except Exception as e:
        print(f"Nie udało się wygenerować wykresu Fouriera: {e}")



if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == "test":
        test_fourier()
        sys.exit(0)
    if len(sys.argv) >= 4 and sys.argv[1] == "anonymize":
        anonymize(sys.argv[2], sys.argv[3])
    else:
        path = sys.argv[1] if len(sys.argv) > 1 else 'Example.png'
        parse(path)