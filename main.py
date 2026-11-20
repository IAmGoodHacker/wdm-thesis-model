"""Розрахунки до магістерської дисертації
“Адаптивні можливості архітектури терміналів транспортних систем електронних комунікацій
за технологією спектрального ущільнення” (В. А. Процюк, ІСЗЗІ КПІ ім. Ігоря Сікорського, 2026).

Запуск:  python main.py            – вивести таблиці розділів 2 і 3
         python main.py --figures  – додатково побудувати рисунки у папці figures/
"""
import sys
import numpy as np

from wdm_model.gn_model import LineParams, p_opt, gsnr_total, gsnr_route_db, lin2db
from wdm_model.modes import (ROUTES, CHANNELS, discrete_mode, pcs_rate, pcs_threshold_db,
                             regenerators_16qam, transponders, years_to_exhaust)
from wdm_model.span_budget import SpanParams, l_max, l_min, l_cd, mean_dgd, l_pmd, p_exceed


def title(t):
    print('\n' + t + '\n' + '-' * len(t))


def chapter2(p=LineParams()):
    title('Параметри ділянки')
    print(f'Втрати ділянки {p.span_loss_db:.1f} дБ, ефективна довжина {p.leff_km:.1f} км, '
          f'|β2| = {p.beta2_s2_per_km * 1e24:.1f} пс²/км')
    for rs in (32e9, 64e9, 95e9):
        print(f'  P_opt ({rs / 1e9:.0f} ГБод) = {10 * np.log10(p_opt(p, rs) * 1e3):.1f} дБм')

    title('Табл. 2.2 – необхідне GSNR для режимів PCS (95 ГБод)')
    for r in range(300, 850, 50):
        print(f'  {r:4d} Гбіт/с: {pcs_threshold_db(r):5.1f} дБ   {r / 112.5:.2f} біт/(с·Гц)')

    title('Табл. 2.3, 2.4 – режими термінала та кількість пар транспондерів на 4 Тбіт/с')
    print(f'{"Маршрут":18s} {"км":>5s} {"GSNR":>5s} {"Б:3R":>5s} {"В":>14s} {"Г":>5s} | A  Б  В  Г')
    cap_b, cap_g, tot = [], [], np.zeros(4, int)
    for name, L in ROUTES:
        g = float(lin2db(gsnr_total(p, int(L / p.span_km))))
        fmt, rb = discrete_mode(g)
        rg = pcs_rate(g)
        reg = regenerators_16qam(L)
        tr = np.array([transponders(4000, 100), transponders(4000, 400, reg + 1),
                       transponders(4000, rb), transponders(4000, rg)])
        tot += tr
        cap_b.append(CHANNELS['В'] * rb / 1000); cap_g.append(CHANNELS['Г'] * rg / 1000)
        print(f'{name:18s} {L:5d} {g:5.1f} {reg:5d} {fmt + " " + str(rb) + "G":>14s} {rg:5d} | '
              + ' '.join(f'{x:2d}' for x in tr))
    print(f'Усього пар транспондерів: А={tot[0]}, Б={tot[1]}, В={tot[2]}, Г={tot[3]}')
    print(f'Середня ємність волокна: А=9,6; В={np.mean(cap_b):.1f}; Г={np.mean(cap_g):.1f} Тбіт/с')

    title('Табл. 2.5 – час до вичерпання ємності (4 Тбіт/с, +30 %/рік)')
    for lab, c in (('А', 9.6), ('В (середнє)', np.mean(cap_b)), ('Г (середнє)', np.mean(cap_g))):
        print(f'  {lab:12s} {c:5.1f} Тбіт/с -> {years_to_exhaust(c):.1f} років')


def chapter3(s=SpanParams(), p=LineParams()):
    title('Підрозділ 3.2 – енергетичний бюджет')
    print(f'L_max = {l_max(s):.1f} км, L_min = {l_min(s):.1f} км')
    title('Табл. 3.2 – вплив рівня передавача')
    for pt in (-3, 0, 3, 5, 10, 13, 17):
        print(f'  {pt:+3d} дБм -> {l_max(s.with_(p_tx_dbm=pt)):.1f} км')
    title('Табл. 3.3 – вплив чутливості приймача')
    for pm in (-18, -24, -28, -32):
        print(f'  {pm} дБм -> {l_max(s.with_(p_min_dbm=pm)):.1f} км')
    title('Табл. 3.4 – втрати на зварному з’єднанні × будівельна довжина')
    for a in (0.02, 0.05, 0.10, 0.15, 0.20):
        print(f'  {a:.2f} дБ: ' + '  '.join(f'{l_max(s.with_(a_splice_db=a, l_build_km=lb)):5.1f}' for lb in (2, 4, 6)))
    title('Табл. 3.6 – коефіцієнт загасання кабелю')
    for a in (0.17, 0.19, 0.22, 0.25, 0.30):
        print(f'  {a:.2f} дБ/км -> {l_max(s.with_(alpha_db=a)):.1f} км')
    title('Табл. 3.7 – хроматична дисперсія')
    for d in (800, 1600, 100):
        print(f'  {d} пс/нм -> {l_cd(d):.0f} км')
    title('Табл. 3.8 – обмеження за PMD, км (2,5 / 10 / 40 Гбіт/с)')
    for q in (1.0, 0.5, 0.2, 0.1):
        print(f'  PMDQ={q}: ' + ' / '.join(f'{l_pmd(b, q):.0f}' for b in (2.5, 10, 40)))
    print(f'  Середня DGD, 560 км, PMDQ=0,5: {mean_dgd(0.5, 560):.1f} пс')
    title('Табл. 3.9 – ймовірність перевищення кратного середнього DGD')
    for r in (2.0, 2.5, 3.0, 3.5, 4.0):
        pr = p_exceed(r)
        print(f'  {r:.1f}: {pr:.1e}  ({pr * 8760:.3g} год/рік)')
    title('Табл. 3.10 – маршрут 560 км: довжина ділянки підсилення')
    for sp in (60, 80, 100, 120, 140):
        g, n = gsnr_route_db(p, 560, sp)
        print(f'  ≤{sp} км: {n} ділянок, GSNR {g:.1f} дБ, {discrete_mode(g)[0]}, PCS {pcs_rate(g)} Гбіт/с')
    title('Табл. 3.11 – маршрут 1040 км: способи збільшення ділянки підсилення')
    from wdm_model.plots import scenarios_3_6
    for name, q in scenarios_3_6(p).items():
        g80, g116 = gsnr_route_db(q, 1040, 80)[0], gsnr_route_db(q, 1040, 116)[0]
        best = max(sp for sp in range(40, 201, 5) if gsnr_route_db(q, 1040, sp)[0] >= 13.5)
        print(f'  {name:36s} {g80:5.1f} {g116:5.1f} дБ, PCS {pcs_rate(g116)} Гбіт/с, '
              f'макс. ділянка для 8QAM ≈ {best} км ({gsnr_route_db(q, 1040, best)[1] - 1} пунктів)')


if __name__ == '__main__':
    chapter2()
    chapter3()
    if '--figures' in sys.argv:
        from wdm_model.plots import all_figures
        all_figures('figures')
        print('\nРисунки збережено в папці figures/')
