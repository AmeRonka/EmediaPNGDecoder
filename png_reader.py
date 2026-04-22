import zlib

# Każdy plik png zaczyna się tą samą sygnaturą. Jeśli sygnatura jest inna to nie jest to png albo jest to uszkodzony
# plik
PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'


#funkcja pomocnicza do odczytywania 4 bajtowych kawałków z początku każdego chunka i crc. PNG używa bigendian
#dlatego czytamy od ostatniego bajtu
def u32(data: bytes, offset: int) -> int:
    return (data[offset] << 24
          | data[offset + 1] << 16
          | data[offset + 2] << 8
          | data[offset + 3])


# analogicznie do u32, ale dla 2-bajtowych liczb (rok w tIME, pola w EXIF/TIFF)
def u16(data: bytes, offset: int) -> int:
    return (data[offset] << 8) | data[offset + 1]


# funkcja pomocnicza sprawdzająca czy pierwsze 8 bajtów pliku odpowiadają sygnaturze PNG
def verify_signature(data: bytes) -> bool:
    return data[:8] == PNG_SIGNATURE


#będziemy się iterować po pliku chunk po chunku zapisując offset w taki sposób żeby
def read_chunk(data: bytes, offset: int) -> tuple:
    length = u32(data, offset)
    chunk_type = data[offset + 4 : offset + 8].decode('ascii')
    chunk_data = data[offset + 8 : offset + 8 + length]
    crc_stored = u32(data, offset + 8 + length)
    crc_computed = zlib.crc32(data[offset + 4 : offset + 8 + length]) & 0xFFFFFFFF
    crc_ok = crc_stored == crc_computed
    return chunk_type, chunk_data, crc_ok, offset + 12 + length
