# yield_curve_simulator.py
# Advanced Yield Curve Deformation Simulator with Historical Scenarios, Bond Impact & PCA

import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
from fredapi import Fred
from dotenv import load_dotenv
from datetime import datetime, timedelta
from sklearn.decomposition import PCA

# === Настройки ===
load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")
if not FRED_API_KEY:
    st.error("❌ FRED_API_KEY не найден. Создайте файл .env с ключом.")
    st.stop()

fred = Fred(api_key=FRED_API_KEY)

TENORS = {
    "1M": 1/12, "3M": 0.25, "6M": 0.5, "1Y": 1.0, "2Y": 2.0,
    "3Y": 3.0, "5Y": 5.0, "7Y": 7.0, "10Y": 10.0, "20Y": 20.0, "30Y": 30.0
}

FRED_SERIES = {
    "1M": "DGS1MO", "3M": "DGS3MO", "6M": "DGS6MO", "1Y": "DGS1",
    "2Y": "DGS2", "3Y": "DGS3", "5Y": "DGS5", "7Y": "DGS7",
    "10Y": "DGS10", "20Y": "DGS20", "30Y": "DGS30"
}

MATURITIES_LIST = np.array(list(TENORS.values()))

# === Функции ===

@st.cache_data(ttl=3600)
def fetch_historical_curve(date_str: str):
    """Получает кривую на конкретную дату."""
    data = {}
    for label, series_id in FRED_SERIES.items():
        try:
            # Запрашиваем данные за ±3 дня, чтобы найти ближайшую торговую дату
            start = (pd.to_datetime(date_str) - timedelta(days=3)).strftime('%Y-%m-%d')
            end = (pd.to_datetime(date_str) + timedelta(days=3)).strftime('%Y-%m-%d')
            series = fred.get_series(series_id, observation_start=start, observation_end=end)
            if not series.empty:
                closest_val = series.dropna().iloc[-1]  # последнее доступное значение
                if pd.notna(closest_val) and closest_val > -10:  # фильтр мусора
                    data[TENORS[label]] = closest_val / 100
        except Exception as e:
            pass
    return data

@st.cache_data(ttl=86400)  # кэш на 1 день
def fetch_pca_data(years=5):
    """Загружает исторические данные для PCA (последние N лет)."""
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365 * years)
    
    all_data = []
    dates = []
    
    # Собираем данные по всем сериям
    series_dict = {}
    for label, series_id in FRED_SERIES.items():
        try:
            s = fred.get_series(series_id, 
                               observation_start=start_date.strftime('%Y-%m-%d'),
                               observation_end=end_date.strftime('%Y-%m-%d'))
            series_dict[label] = s
        except:
            continue
    
    # Выравниваем по датам
    common_dates = None
    for s in series_dict.values():
        if common_dates is None:
            common_dates = set(s.dropna().index)
        else:
            common_dates &= set(s.dropna().index)
    
    common_dates = sorted(common_dates)[-1000:]  # последние 1000 торговых дней
    
    for date in common_dates:
        row = []
        valid = True
        for label in FRED_SERIES.keys():
            val = series_dict[label].get(date, np.nan)
            if pd.isna(val) or val < -10:
                valid = False
                break
            row.append(val / 100)
        if valid:
            all_data.append(row)
            dates.append(date)
    
    return np.array(all_data), dates

def interpolate_curve(maturities, yields, fine_grid):
    if len(maturities) < 2:
        return np.full_like(fine_grid, np.nan)
    spline = CubicSpline(maturities, yields, bc_type='natural')
    return spline(fine_grid)

def apply_deformations(base_yields, maturities_fine, shift, steep, butterfly_amp):
    shifted = base_yields + shift / 10000
    slope_effect = (maturities_fine - np.min(maturities_fine)) / (np.max(maturities_fine) - np.min(maturities_fine))
    shifted += steep / 10000 * slope_effect
    butterfly_shape = np.exp(-0.5 * ((maturities_fine - 5.0) / 3.0) ** 2)
    shifted += butterfly_amp / 10000 * butterfly_shape
    return np.maximum(shifted, -0.05)

def bond_price_and_duration(cash_flows, times, yield_curve_func):
    """Рассчитывает цену и дюрацию облигации."""
    y = yield_curve_func(times)
    discount_factors = np.exp(-y * times)
    pv = cash_flows * discount_factors
    price = np.sum(pv)
    macaulay_duration = np.sum(times * pv) / price
    modified_duration = macaulay_duration / (1 + np.mean(y))
    return price, macaulay_duration, modified_duration

# === Streamlit App ===
st.set_page_config(page_title="Advanced Yield Curve Simulator", layout="wide")
st.title("📉 Advanced Yield Curve Deformation Simulator")
st.markdown("""
*Интерактивный анализ кривой доходности: исторические сценарии, воздействие на облигации, PCA-факторы.*
""")

# Вкладки
tab1, tab2, tab3 = st.tabs(["📊 Основной симулятор", "🏦 Влияние на облигацию", "🔬 PCA-анализ"])

# === ВКЛАДКА 1: Основной симулятор ===
with tab1:
    st.subheader("Выберите дату для загрузки исторической кривой")
    default_date = datetime(2025, 1, 10)
    selected_date = st.date_input("Дата", value=default_date, min_value=datetime(2000,1,1), max_value=datetime.today())
    
    raw_data = fetch_historical_curve(str(selected_date))
    if not raw_data:
        st.error(f"❌ Данные за {selected_date} не найдены. Попробуйте другую дату (лучше будний день).")
        st.stop()
    
    maturities_raw = np.array(list(raw_data.keys()))
    yields_raw = np.array(list(raw_data.values()))
    maturities_fine = np.linspace(0.08, 30, 300)
    yields_fine = interpolate_curve(maturities_raw, yields_raw, maturities_fine)
    
    st.sidebar.header("🔧 Деформации")
    shift_bps = st.sidebar.slider("Параллельный сдвиг (bps)", -200, 200, 0, step=5)
    steep_bps = st.sidebar.slider("Наклон (bps)", -150, 150, 0, step=5)
    butterfly_bps = st.sidebar.slider("Выпуклость (bps)", -100, 100, 0, step=5)
    
    deformed_yields = apply_deformations(yields_fine, maturities_fine, shift_bps, steep_bps, butterfly_bps)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(maturities_fine, yields_fine * 100, 'o-', label='Оригинал', color='steelblue')
    ax.plot(maturities_fine, deformed_yields * 100, '--', label='Деформированная', color='crimson')
    ax.set_xlabel("Срок (лет)"); ax.set_ylabel("Доходность (%)")
    ax.set_title(f"Кривая доходности на {selected_date}")
    ax.grid(True, linestyle='--', alpha=0.6); ax.legend(); ax.set_ylim(bottom=-1)
    st.pyplot(fig)
    
    df_display = pd.DataFrame({
        "Срок": list(TENORS.keys()),
        "Лет": [TENORS[k] for k in TENORS],
        "Доходность (%)": [raw_data.get(TENORS[k], np.nan) * 100 for k in TENORS]
    }).dropna().round(3)
    st.dataframe(df_display, use_container_width=True)

# === ВКЛАДКА 2: Облигация ===
with tab2:
    st.subheader("Оценка влияния деформации на облигацию")
    
    col1, col2 = st.columns(2)
    with col1:
        coupon_rate = st.number_input("Купон (% годовых)", min_value=0.0, max_value=20.0, value=5.0, step=0.5) / 100
        maturity_bond = st.number_input("Срок погашения (лет)", min_value=1.0, max_value=30.0, value=10.0, step=1.0)
        face_value = st.number_input("Номинал", min_value=100, max_value=10000, value=1000, step=100)
    
    # Генерация денежных потоков
    periods = int(maturity_bond)
    cash_flows = np.full(periods, coupon_rate * face_value)
    cash_flows[-1] += face_value
    times_cf = np.arange(1, periods + 1)
    
    # Получаем базовую кривую (на сегодня)
    today_data = fetch_historical_curve(str(datetime.today().date()))
    if not today_data:
        st.warning("Не удалось загрузить текущую кривую для расчёта.")
    else:
        # Интерполятор
        interp_orig = CubicSpline(list(today_data.keys()), list(today_data.values()), bc_type='natural')
        
        # Цена и дюрация до деформации
        price_orig, mac_orig, mod_orig = bond_price_and_duration(cash_flows, times_cf, interp_orig)
        
        # Применяем деформацию к кривой
        maturities_fine = np.linspace(0.08, 30, 300)
        yields_fine = interpolate_curve(list(today_data.keys()), list(today_data.values()), maturities_fine)
        deformed_yields = apply_deformations(yields_fine, maturities_fine, shift_bps, steep_bps, butterfly_bps)
        interp_deformed = CubicSpline(maturities_fine, deformed_yields, bc_type='natural')
        
        # После деформации
        price_new, mac_new, mod_new = bond_price_and_duration(cash_flows, times_cf, interp_deformed)
        
        st.metric("Цена облигации (до)", f"${price_orig:.2f}", delta=None)
        st.metric("Цена облигации (после)", f"${price_new:.2f}", delta=f"{price_new - price_orig:.2f}")
        st.metric("Модифицированная дюрация", f"{mod_new:.2f} лет")
        st.info(f"Изменение цены ≈ –{mod_new:.2f} × Δy. Это мера чувствительности к изменению ставок.")

# === ВКЛАДКА 3: PCA ===
with tab3:
    st.subheader("PCA: Главные компоненты движения кривой")
    st.markdown("""
    > 90% изменений кривой доходности объясняются тремя факторами:
    > - **Level (уровень)** — параллельный сдвиг
    > - **Slope (наклон)** — разница короткие/длинные ставки
    > - **Curvature (выпуклость)** — движение средних сроков
    """)
    
    with st.spinner("Загрузка исторических данных для PCA..."):
        pca_data, pca_dates = fetch_pca_data(years=5)
    
    if len(pca_data) < 10:
        st.error("Недостаточно данных для PCA.")
    else:
        # Выполняем PCA
        pca = PCA(n_components=3)
        components = pca.fit_transform(pca_data)
        explained = pca.explained_variance_ratio_
        
        st.write(f"Объяснённая дисперсия: Level = {explained[0]:.1%}, Slope = {explained[1]:.1%}, Curvature = {explained[2]:.1%}")
        
        # График факторов
        fig_pca, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
        labels = ["Level (параллельный)", "Slope (наклон)", "Curvature (выпуклость)"]
        colors = ["tab:blue", "tab:orange", "tab:green"]
        for i in range(3):
            axs[i].plot(pca_dates[-200:], components[-200:, i], color=colors[i])
            axs[i].set_ylabel(labels[i])
            axs[i].grid(True, alpha=0.4)
        axs[2].set_xlabel("Дата")
        plt.tight_layout()
        st.pyplot(fig_pca)
        
        # Форма компонент
        fig_comp, axc = plt.subplots(figsize=(8, 4))
        for i in range(3):
            axc.plot(MATURITIES_LIST, pca.components_[i], 'o-', label=labels[i])
        axc.set_xlabel("Срок (лет)"); axc.set_ylabel("Вклад в компоненту")
        axc.legend(); axc.grid(True, alpha=0.4)
        st.pyplot(fig_comp)

st.markdown("---")
st.caption("Данные: Federal Reserve Economic Data (FRED). Проект создан для образовательных целей.")