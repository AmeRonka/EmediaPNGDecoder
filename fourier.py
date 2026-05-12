import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def display_image_and_fourier(image_path: str) -> None:
    print("\nWczytywanie pikseli obrazu i obliczanie transformacji Fouriera...")
    #Wczytanie obrazu i konwersja do skali szarości (luminancji) dla analizy widma
    img = Image.open(image_path).convert('L')
    img_data = np.asarray(img)

    #2D Transformata Fouriera
    f_transform = np.fft.fft2(img_data)
    #Przesunięcie zerowych częstotliwości na środek widma
    f_shift = np.fft.fftshift(f_transform)
    
    #Obliczenie widma amplitudowego (skala logarytmiczna dla lepszej widoczności)
    #Dodajemy 1, aby uniknąć log(0)
    magnitude_spectrum = 20 * np.log(np.abs(f_shift) + 1)

    plt.figure(figsize=(12, 6))
    
    plt.subplot(121)
    plt.imshow(img_data, cmap='gray')
    plt.title('Oryginalny obraz (skala szarości)')
    plt.axis('off')
    
    plt.subplot(122)
    plt.imshow(magnitude_spectrum, cmap='gray')
    plt.title('Widmo amplitudowe (FFT)')
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()

def test_fourier() -> None:
    print("Uruchamianie testów transformacji Fouriera...")
    
    #Impuls Diraca (jeden jasny piksel na czarnym tle)
    #Zgodnie z teorią sygnałów, transformata Fouriera impulsu Diraca to 
    #widmo płaskie (stała wartość)
    test_img = np.zeros((100, 100))
    test_img[50, 50] = 255
    
    f_transform = np.fft.fft2(test_img)
    magnitude = np.abs(f_transform)
    
    #Sprawdzamy, czy wszystkie wartości w widmie amplitudowym są w przybliżeniu równe
    if np.allclose(magnitude, magnitude[0, 0]):
        print("  OK Test impulsu Diraca: Widmo jest stałe")
    else:
        print("  BŁĄD Test impulsu Diraca nie przeszedł.")

    #Odwrotna transformata Fouriera (IFFT)
    #Sprawdzamy, czy powrót z domeny częstotliwości do przestrzennej odtworzy oryginał
    inverse_img = np.fft.ifft2(f_transform).real
    if np.allclose(test_img, inverse_img):
        print("  OK Udało się odzyskać oryginalny obraz z domeny częstotliwości")
    else:
        print("  BŁĄD Test IFFT nie przeszedł.")