"""Модель оптичної лінії на основі GN-моделі (підрозділ 2.2 магістерської дисертації).

Формули: (2.1) шум ASE, (2.2) спектральна щільність NLI, (2.3) ефективна довжина,
(2.4) GSNR лінії з N ділянок, (2.5) урахування власного ВСШ трансивера,
(2.6) оптимальна потужність на канал.
"""
from dataclasses import dataclass, replace
import numpy as np

H = 6.62607015e-34       # стала Планка, Дж·с
C = 2.99792458e8         # швидкість світла, м/с


def db2lin(x):
    return 10.0 ** (np.asarray(x) / 10.0)


def lin2db(x):
    return 10.0 * np.log10(x)


@dataclass(frozen=True)
class LineParams:
    """Параметри лінії (базовий варіант – табл. 1.2 і підрозділ 2.1)."""
    alpha_db: float = 0.22        # коефіцієнт загасання, дБ/км
    disp: float = 17.0            # коефіцієнт хроматичної дисперсії, пс/(нм·км)
    gamma: float = 1.3            # коефіцієнт нелінійності, 1/(Вт·км)
    span_km: float = 80.0         # довжина підсилювальної ділянки, км
    extra_loss_db: float = 3.0    # додаткові втрати ділянки (зварні, роз'єми, запас), дБ
    nf_db: float = 5.5            # коефіцієнт шуму EDFA (або еквівалентний NF ділянки), дБ
    bwdm_hz: float = 4.8e12       # ширина зайнятого спектра (C-діапазон), Гц
    snr_trx_db: float = 21.0      # власне ВСШ трансивера, дБ
    wavelength_m: float = 1550e-9

    def with_(self, **kw):
        return replace(self, **kw)

    # --- похідні величини
    @property
    def span_loss_db(self):
        return self.alpha_db * self.span_km + self.extra_loss_db

    @property
    def alpha_field(self):
        """коефіцієнт загасання за полем, 1/км"""
        return self.alpha_db / (20.0 * np.log10(np.e))

    @property
    def leff_km(self):
        """ефективна довжина ділянки, формула (2.3)"""
        a = self.alpha_field
        return (1.0 - np.exp(-2.0 * a * self.span_km)) / (2.0 * a)

    @property
    def leff_a_km(self):
        return 1.0 / (2.0 * self.alpha_field)

    @property
    def beta2_s2_per_km(self):
        """|β2| за формулою (1.6), с²/км"""
        d = self.disp * 1e-12 / 1e-9  # с/(м·км)
        return d * self.wavelength_m ** 2 / (2.0 * np.pi * C)


def p_ase(p: LineParams, rs_hz: float) -> float:
    """потужність ASE одного підсилювача в смузі Rs, Вт – формула (2.1)"""
    nu = C / p.wavelength_m
    return db2lin(p.nf_db) * H * nu * db2lin(p.span_loss_db) * rs_hz


def eta_nli(p: LineParams, rs_hz: float) -> float:
    """коефіцієнт η у P_NLI = η·P³ для однієї ділянки, 1/Вт² – формула (2.2)"""
    b2, la = p.beta2_s2_per_km, p.leff_a_km
    g_nli_coef = (8.0 / 27.0) * p.gamma ** 2 * p.leff_km ** 2 * \
        np.arcsinh(np.pi ** 2 / 2.0 * b2 * la * p.bwdm_hz ** 2) / (np.pi * b2 * la)
    # G_NLI = coef · (P/Rs)³ ;  P_NLI = G_NLI · Rs = coef · P³ / Rs²
    return g_nli_coef / rs_hz ** 2


def p_opt(p: LineParams, rs_hz: float) -> float:
    """оптимальна потужність на канал, Вт – формула (2.6)"""
    return (p_ase(p, rs_hz) / (2.0 * eta_nli(p, rs_hz))) ** (1.0 / 3.0)


def gsnr_line(p: LineParams, n_spans: int, p_ch: float, rs_hz: float = 64e9) -> float:
    """GSNR лінії (лінійні одиниці) – формула (2.4)"""
    return p_ch / (n_spans * (p_ase(p, rs_hz) + eta_nli(p, rs_hz) * p_ch ** 3))


def gsnr_total(p: LineParams, n_spans: int, p_ch: float = None, rs_hz: float = 64e9) -> float:
    """GSNR з урахуванням трансивера (лінійні одиниці) – формула (2.5).
    Якщо потужність не задано, використовується оптимальна."""
    if p_ch is None:
        p_ch = p_opt(p, rs_hz)
    return 1.0 / (1.0 / gsnr_line(p, n_spans, p_ch, rs_hz) + 1.0 / db2lin(p.snr_trx_db))


def gsnr_route_db(p: LineParams, length_km: float, max_span_km: float = None, rs_hz: float = 64e9) -> float:
    """GSNR маршруту, поділеного на однакові ділянки довжиною не більше max_span_km (підрозділ 3.6)"""
    if max_span_km is None:
        max_span_km = p.span_km
    n = int(np.ceil(length_km / max_span_km - 1e-9))
    q = p.with_(span_km=length_km / n)
    return float(lin2db(gsnr_total(q, n, rs_hz=rs_hz))), n
