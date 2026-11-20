"""Розрахунок довжини ділянки (розділ 3): енергетичний бюджет (3.1)–(3.5),
дисперсійні обмеження (3.6)–(3.8), статистика DGD (3.9)."""
from dataclasses import dataclass, replace
import numpy as np
from scipy import integrate


@dataclass(frozen=True)
class SpanParams:
    """вихідні дані базового варіанта (табл. 3.1)"""
    p_tx_dbm: float = 0.0       # рівень передавача
    p_min_dbm: float = -24.0    # чутливість приймача
    p_max_dbm: float = -7.0     # рівень перевантаження приймача
    alpha_db: float = 0.22      # дБ/км
    l_build_km: float = 4.0     # будівельна довжина кабелю
    a_splice_db: float = 0.05   # втрати на зварному з'єднанні
    n_conn: int = 4             # кількість роз'ємних з'єднань
    a_conn_db: float = 0.5      # втрати на роз'ємному з'єднанні
    margin_db: float = 3.0      # експлуатаційний запас

    def with_(self, **kw):
        return replace(self, **kw)


def l_max(s: SpanParams) -> float:
    """максимальна довжина ділянки за енергетичним бюджетом – формула (3.4)"""
    e = s.p_tx_dbm - s.p_min_dbm                      # (3.1)
    return (e - s.n_conn * s.a_conn_db - s.margin_db + s.a_splice_db) / \
        (s.alpha_db + s.a_splice_db / s.l_build_km)


def l_min(s: SpanParams) -> float:
    """мінімальна довжина ділянки (обмеження перевантаженням) – формула (3.5)"""
    return (s.p_tx_dbm - s.p_max_dbm - s.n_conn * s.a_conn_db + s.a_splice_db) / \
        (s.alpha_db + s.a_splice_db / s.l_build_km)


def level_diagram(s: SpanParams, length_km: float, step_km: float = 0.05):
    """діаграма рівнів уздовж ділянки (рис. 3.1)"""
    z = np.arange(0, length_km + step_km, step_km)
    level = s.p_tx_dbm - s.n_conn / 2 * s.a_conn_db - s.alpha_db * z
    splices = np.floor(z / s.l_build_km - 1e-9)
    splices = np.clip(splices, 0, length_km / s.l_build_km - 1)
    level -= splices * s.a_splice_db
    level[-1] -= s.n_conn / 2 * s.a_conn_db
    return z, level


def l_cd(d_allowed_ps_nm: float, disp: float = 17.0) -> float:
    """довжина за хроматичною дисперсією – формула (3.6)"""
    return d_allowed_ps_nm / disp


def mean_dgd(pmd_q: float, length_km: float) -> float:
    """середня DGD лінії, пс – формула (3.7)"""
    return pmd_q * np.sqrt(length_km)


def l_pmd(bitrate_gbps: float, pmd_q: float, fraction: float = 0.1) -> float:
    """довжина за PMD для прямого детектування – формула (3.8)"""
    t_bit_ps = 1000.0 / bitrate_gbps
    return (fraction * t_bit_ps / pmd_q) ** 2


def maxwell_pdf(dt, mean):
    """розподіл Максвелла миттєвої DGD – формула (3.9)"""
    sigma = mean * np.sqrt(np.pi / 8.0)
    return np.sqrt(2 / np.pi) * dt ** 2 / sigma ** 3 * np.exp(-dt ** 2 / (2 * sigma ** 2))


def p_exceed(ratio: float) -> float:
    """ймовірність, що миттєва DGD перевищить ratio·<DGD> (табл. 3.9)"""
    val, _ = integrate.quad(lambda x: maxwell_pdf(x, 1.0), ratio, np.inf)
    return val
