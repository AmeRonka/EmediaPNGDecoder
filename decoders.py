from png_reader import u16, u32
from exif import decode_exif


def decode_ihdr(data: bytes) -> None:
    color_type_names = {
        0: "Greyscale",
        2: "RGB",
        3: "Indexed (paleta)",
        4: "Greyscale + Alpha",
        6: "RGBA",
    }
    interlace_names = {
        0: "brak",
        1: "Adam7",
    }

    width = u32(data, 0)
    height = u32(data, 4)
    bit_depth = data[8]
    color_type = data[9]
    compression = data[10]
    filter_method = data[11]
    interlace = data[12]

    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color_type]
    bpp = bit_depth * channels

    print(f"  Rozmiar:        {width} x {height} px")
    print(f"  Bit depth:      {bit_depth} bit/kanał")
    print(f"  Typ koloru:     {color_type} — {color_type_names.get(color_type, '???')}")
    print(f"  Kanały:         {channels}")
    print(f"  Głębia koloru:  {bpp} bit/piksel")
    print(f"  Kompresja:      {compression} (deflate)")
    print(f"  Filtrowanie:    {filter_method}")
    print(f"  Interlace:      {interlace} — {interlace_names.get(interlace, '???')}")


def decode_text(data: bytes) -> None:
    null_pos = data.index(0)
    keyword = data[:null_pos].decode('latin-1')
    text = data[null_pos + 1:].decode('latin-1')
    print(f"  Keyword: {keyword!r}")
    print(f"  Text:    {text!r}")


def decode_phys(data: bytes) -> None:
    ppu_x = u32(data, 0)
    ppu_y = u32(data, 4)
    unit = data[8]

    if unit == 0:
        print(f"  Proporcje piksela: {ppu_x}:{ppu_y} (jednostka nieznana)")
    elif unit == 1:
        dpi_x = ppu_x * 0.0254
        dpi_y = ppu_y * 0.0254
        print(f"  Rozdzielczość: {ppu_x} x {ppu_y} pikseli/metr  "
              f"(~ {dpi_x:.1f} x {dpi_y:.1f} DPI)")
    else:
        print(f"  Jednostka nieznana: {unit}")


def decode_time(data: bytes) -> None:
    year = u16(data, 0)
    month = data[2]
    day = data[3]
    hour = data[4]
    minute = data[5]
    second = data[6]
    print(f"  Data modyfikacji: "
          f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d} UTC")


def decode_plte(data: bytes) -> None:
    if len(data) % 3 != 0:
        print(f"  BŁĄD: długość PLTE ({len(data)}) nie jest podzielna przez 3!")
        return

    num_colors = len(data) // 3
    print(f"  Paleta: {num_colors} kolorów")
    for i in range(num_colors):
        r = data[i * 3]
        g = data[i * 3 + 1]
        b = data[i * 3 + 2]
        print(f"    [{i:>3}] R={r:>3} G={g:>3} B={b:>3}")


# Mapowanie typu chunka na funkcję dekodującą. Łatwo dodać kolejne wpisy.
DECODERS = {
    "IHDR": decode_ihdr,
    "PLTE": decode_plte,
    "tEXt": decode_text,
    "pHYs": decode_phys,
    "tIME": decode_time,
    "eXIf": decode_exif,
}
