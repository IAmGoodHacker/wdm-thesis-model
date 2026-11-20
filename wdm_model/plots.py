"""Побудова рисунків розділів 2 і 3 (рис. 2.1–2.4, 3.1–3.7)."""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from .gn_model import LineParams, p_ase, eta_nli, p_opt, gsnr_total, gsnr_route_db, lin2db
from .modes import FORMATS_64G, ROUTES, CHANNELS, discrete_mode, pcs_rate
from .span_budget import SpanParams, l_max, level_diagram, mean_dgd, maxwell_pdf

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.grid': True, 'grid.alpha': 0.3})


def _save(fig, out, name):
    os.makedirs(out, exist_ok=True)
    fig.tight_layout()
    fig.savefig(os.path.join(out, name), dpi=200)
    plt.close(fig)


def fig_2_1(p, out):
    rs = 64e9
    pdbm = np.linspace(-6, 8, 200)
    pw = 1e-3 * 10 ** (pdbm / 10)
    g = [lin2db(gsnr_total(p, 7, x, rs)) for x in pw]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(pdbm, g, lw=2)
    po = 10 * np.log10(p_opt(p, rs) * 1e3)
    ax.axvline(po, ls='--', c='gray')
    ax.set_xlabel('Потужність на канал, дБм'); ax.set_ylabel('GSNR, дБ')
    ax.set_title('Маршрут Київ – Львів, 7 ділянок, 64 ГБод')
    _save(fig, out, 'fig_2_1_gsnr_vs_power.png')


def fig_2_2(p, out):
    n = np.arange(1, 21)
    g = [lin2db(gsnr_total(p, k)) for k in n]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(n * p.span_km, g, 'o-', lw=2, label='GSNR')
    for name, _, req in FORMATS_64G:
        ax.axhline(req, ls='--', lw=1); ax.text(n[-1] * p.span_km, req + 0.15, name, ha='right')
    ax.set_xlabel('Довжина маршруту, км'); ax.set_ylabel('GSNR, дБ'); ax.legend()
    _save(fig, out, 'fig_2_2_gsnr_vs_length.png')


def fig_2_3(p, out):
    names = [r[0] for r in ROUTES]
    g = [lin2db(gsnr_total(p, int(L / p.span_km))) for _, L in ROUTES]
    a = [CHANNELS['А'] * 0.1 for _ in g]
    b = [CHANNELS['В'] * discrete_mode(x)[1] / 1000 for x in g]
    c = [CHANNELS['Г'] * pcs_rate(x) / 1000 for x in g]
    x = np.arange(len(names)); w = 0.27
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(x - w, a, w, label='А – фіксована 100G')
    ax.bar(x, b, w, label='В – адаптивна, дискретні формати')
    ax.bar(x + w, c, w, label='Г – адаптивна з PCS')
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=35, ha='right')
    ax.set_ylabel('Ємність волокна, Тбіт/с'); ax.legend()
    _save(fig, out, 'fig_2_3_capacity_by_route.png')


def fig_2_4(p, out):
    shifts = np.linspace(-1, 2, 13)
    avg_b, avg_g = [], []
    for s in shifts:
        g = [lin2db(gsnr_total(p, int(L / p.span_km))) for _, L in ROUTES]
        avg_b.append(np.mean([CHANNELS['В'] * discrete_mode(x, s)[1] / 1000 for x in g]))
        avg_g.append(np.mean([CHANNELS['Г'] * pcs_rate(x, margin_shift_db=s) / 1000 for x in g]))
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.step(shifts, avg_b, where='mid', lw=2, label='Архітектура В')
    ax.plot(shifts, avg_g, 'o-', lw=2, label='Архітектура Г')
    ax.set_xlabel('Зміна системного запасу відносно 2 дБ, дБ'); ax.set_ylabel('Середня ємність, Тбіт/с'); ax.legend()
    _save(fig, out, 'fig_2_4_capacity_vs_margin.png')


def fig_3_1(s, out):
    z, lev = level_diagram(s, 80)
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(z, lev, lw=2)
    ax.axhline(s.p_min_dbm, ls='--', c='r', label='Чутливість приймача')
    ax.axhline(s.p_min_dbm + s.margin_db, ls=':', c='orange', label='Чутливість + запас')
    ax.set_xlabel('Відстань, км'); ax.set_ylabel('Рівень, дБм'); ax.legend()
    _save(fig, out, 'fig_3_1_level_diagram.png')


def fig_3_2(s, out):
    ptx = np.linspace(-3, 17, 50)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for pmin in (-18, -24, -28, -32):
        ax.plot(ptx, [l_max(s.with_(p_tx_dbm=x, p_min_dbm=pmin)) for x in ptx], lw=2, label=f'Pmin = {pmin} дБм')
    ax.set_xlabel('Рівень передавача, дБм'); ax.set_ylabel('Довжина ділянки, км'); ax.legend()
    _save(fig, out, 'fig_3_2_length_vs_tx.png')


def fig_3_3(s, out):
    a = np.linspace(0.02, 0.2, 40)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for lb in (2, 4, 6):
        ax.plot(a, [l_max(s.with_(a_splice_db=x, l_build_km=lb)) for x in a], lw=2, label=f'будівельна довжина {lb} км')
    ax.set_xlabel('Втрати на зварному з’єднанні, дБ'); ax.set_ylabel('Довжина ділянки, км'); ax.legend()
    _save(fig, out, 'fig_3_3_length_vs_splice.png')


def fig_3_4(out):
    L = np.linspace(1, 3000, 400)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for q in (1.0, 0.5, 0.2, 0.1):
        ax.plot(L, mean_dgd(q, L), lw=2, label=f'PMDQ = {q} пс/√км')
    for v, lab in ((40, '2,5 Гбіт/с'), (10, '10 Гбіт/с'), (2.5, '40 Гбіт/с'), (30, 'когерентний 100G')):
        ax.axhline(v, ls='--', lw=1); ax.text(L[-1], v * 1.05, lab, ha='right')
    ax.set_yscale('log'); ax.set_xlabel('Довжина лінії, км'); ax.set_ylabel('Середня DGD, пс'); ax.legend()
    _save(fig, out, 'fig_3_4_dgd_vs_length.png')


def fig_3_5(out):
    x = np.linspace(0, 40, 400)
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(x, maxwell_pdf(x, 10.0), lw=2)
    ax.set_xlabel('Миттєва DGD, пс'); ax.set_ylabel('Густина ймовірності, 1/пс')
    _save(fig, out, 'fig_3_5_maxwell.png')


def scenarios_3_6(p):
    """способи зменшення шуму ділянки (табл. 3.11)"""
    g654 = dict(alpha_db=0.17, gamma=0.8, disp=21.0)
    return {
        'Базовий: G.652.D, EDFA (NF 5,5 дБ)': p,
        'EDFA з NF 4,5 дБ': p.with_(nf_db=4.5),
        'Якісний монтаж (1,5 дБ)': p.with_(extra_loss_db=1.5),
        'Гібридне раманівське + EDFA': p.with_(nf_db=2.5),
        'Волокно G.654.E': p.with_(**g654),
        'G.654.E + раманівське': p.with_(nf_db=2.5, **g654),
    }


def fig_3_6(p, out):
    spans = np.arange(50, 181, 2)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    for name, q in scenarios_3_6(p).items():
        ax.plot(spans, [gsnr_route_db(q, 1040, s)[0] for s in spans], lw=2, label=name)
    ax.axhline(13.5, ls='--', c='k', lw=1); ax.text(180, 13.7, 'поріг 8QAM', ha='right')
    ax.set_xlabel('Максимальна довжина ділянки, км'); ax.set_ylabel('GSNR маршруту 1040 км, дБ'); ax.legend(fontsize=8)
    _save(fig, out, 'fig_3_6_gsnr_vs_span.png')


def fig_3_7(s, out):
    base = l_max(s)
    items = [('Передпідсилювач EDFA', l_max(s.with_(p_min_dbm=-32))),
             ('Лавинний фотодіод замість PIN', l_max(s) - l_max(s.with_(p_min_dbm=-18)) + base),
             ('Бустер +5 дБм', l_max(s.with_(p_tx_dbm=5))),
             ('Кабель 0,19 дБ/км', l_max(s.with_(alpha_db=0.19))),
             ('2 роз’єми замість 4', l_max(s.with_(n_conn=2))),
             ('Роз’єми 0,25 дБ', l_max(s.with_(a_conn_db=0.25))),
             ('Зварювання 0,02 дБ', l_max(s.with_(a_splice_db=0.02))),
             ('Будівельна довжина 6 км', l_max(s.with_(l_build_km=6)))]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.barh([i[0] for i in items][::-1], [i[1] - base for i in items][::-1])
    ax.set_xlabel('Приріст довжини ділянки, км')
    _save(fig, out, 'fig_3_7_span_gain.png')


def all_figures(out='figures'):
    p, s = LineParams(), SpanParams()
    fig_2_1(p, out); fig_2_2(p, out); fig_2_3(p, out); fig_2_4(p, out)
    fig_3_1(s, out); fig_3_2(s, out); fig_3_3(s, out); fig_3_4(out); fig_3_5(out); fig_3_6(p, out); fig_3_7(s, out)
