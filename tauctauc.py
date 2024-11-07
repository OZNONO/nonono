Python 3.12.0 (tags/v3.12.0:0fb18b0, Oct  2 2023, 13:03:39) [MSC v.1935 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> import numpy as np
... import pandas as pd
... import matplotlib.pyplot as plt
... from scipy.optimize import curve_fit
... 
... # 데이터 파일 읽기
... file_path = '/mnt/data/50-1.txt'
... data = pd.read_csv(file_path, delimiter='\t', skiprows=0, usecols=[1, 2], names=['Wavelength', 'Absorbance'])
... 
... # 파장과 흡광도 데이터
... wavelength = data['Wavelength'].values
... absorbance = data['Absorbance'].values
... 
... # 코팅된 물질의 두께 (cm)
... d = 1e-5  # 100 nm
... 
... # 파장에서 에너지(hv) 계산 (eV)
... h = 6.626e-34  # Planck's constant (J*s)
... c = 3.0e8  # Speed of light (m/s)
... eV = 1.602e-19  # 1 eV in Joules
... 
... energy = (h * c) / (wavelength * 1e-9) / eV
... 
... # 흡수 계수(α) 계산 (단위 변환 포함)
... alpha = 2.303 * absorbance / d
... 
... # Tauc plot 데이터 (직접 전이 가정, n=1/2)
... tauc_y = (alpha * energy)**0.5
... 
... # Tauc plot 그리기
... plt.figure(figsize=(10, 6))
... plt.plot(energy, tauc_y, 'o-', label='Tauc plot (n=1/2)')
... 
... # 선형 구간 선택 (에너지 범위 설정 필요)
... linear_range = (energy > 3.0) & (energy < 3.5)  # 예시로 3.0~3.5 eV 범위 선택
... x_linear = energy[linear_range]
y_linear = tauc_y[linear_range]

# 선형 회귀
def linear_fit(x, a, b):
    return a * x + b

params, _ = curve_fit(linear_fit, x_linear, y_linear)
a, b = params

# 직선 외삽
plt.plot(x_linear, linear_fit(x_linear, a, b), 'r--', label='Linear fit')

# 밴드 갭 추정
band_gap = -b / a
plt.axvline(x=band_gap, color='g', linestyle='--', label=f'Band gap = {band_gap:.2f} eV')

# 그래프 설정
plt.xlabel('Energy (eV)')
plt.ylabel('$(αhv)^{1/2}$ (a.u.)')
plt.title('Tauc Plot for Band Gap Determination')
plt.legend()
plt.grid(True)
plt.show()

print(f"Estimated Band Gap: {band_gap:.2f} eV")
