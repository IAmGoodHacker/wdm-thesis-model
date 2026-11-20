"""Вибір режиму роботи термінала (табл. 1.6, 2.2) і порівняння архітектур А–Г (підрозділ 2.4)."""
import numpy as np

# Необхідне GSNR для дискретних форматів, 64 ГБод (табл. 1.6): назва, Гбіт/с, дБ
FORMATS_64G = [('DP-16QAM', 400, 16.5), ('DP-8QAM', 300, 13.5), ('DP-QPSK', 200, 9.5)]

# Маршрути магістральної мережі (табл. 2.1): назва, довжина, км
ROUTES = [('Київ – Житомир', 160), ('Київ – Вінниця', 240), ('Київ – Полтава', 400),
          ('Київ – Дніпро', 480), ('Київ – Одеса', 480), ('Київ – Львів', 560),
          ('Київ – Ужгород', 800), ('Харків – Одеса', 880), ('Львів – Харків', 1040)]

# Архітектури (підрозділ 2.1): кількість каналів у C-діапазоні
CHANNELS = {'А': 96, 'Б': 64, 'В': 64, 'Г': 42}


def discrete_mode(gsnr_db, margin_shift_db=0.0):
    """архітектура В: формат з найбільшою швидкістю, для якого GSNR ≥ GSNR_req"""
    for name, rate, req in FORMATS_64G:
        if gsnr_db >= req + margin_shift_db:
            return name, rate
    return None, 0


def pcs_rate(gsnr_db, rs_gbd=95.0, gap_db=4.5, r_ov=0.8, max_bits=6.0, step=50, max_rate=800,
             margin_shift_db=0.0):
    """архітектура Г: швидкість PCS-каналу за наближенням (1.11), округлення вниз до кроку 50 Гбіт/с"""
    snr = 10 ** ((gsnr_db - margin_shift_db) / 10)
    gap = 10 ** (gap_db / 10)
    bits = min(np.log2(1 + snr / gap), max_bits)
    rb = 2 * rs_gbd * bits * r_ov
    return int(min(np.floor(rb / step + 1e-9) * step, max_rate))


def pcs_threshold_db(rate, rs_gbd=95.0, gap_db=4.5, r_ov=0.8):
    """необхідне GSNR для заданої швидкості PCS-каналу (табл. 2.2)"""
    bits = rate / (2 * rs_gbd * r_ov)
    return 10 * np.log10((2 ** bits - 1) * 10 ** (gap_db / 10))


def regenerators_16qam(length_km, reach_km=320):
    """архітектура Б: кількість вузлів 3R, щоб жоден сегмент не перевищував дальності 16QAM"""
    return int(np.ceil(length_km / reach_km - 1e-9)) - 1


def transponders(traffic_gbps, rate_gbps, segments=1):
    """кількість пар транспондерів для заданого трафіку (табл. 2.4)"""
    return int(np.ceil(traffic_gbps / rate_gbps - 1e-9)) * segments


def years_to_exhaust(c_max, c0=4.0, growth=0.30):
    """час до вичерпання ємності волокна – формула (2.7)"""
    return np.log(c_max / c0) / np.log(1 + growth)
