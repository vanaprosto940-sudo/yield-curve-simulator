# Yield Curve Deformation Simulator

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Interactive_UI-green)](https://streamlit.io)

An advanced, interactive tool for visualizing U.S. Treasury yield curve deformations, analyzing bond sensitivity, and exploring principal components of yield curve dynamics. Built for educational and research purposes by a high school student Belous Ivan.

> **"Understanding the yield curve is understanding the heartbeat of the global economy."**

---

## 🔍 Overview

This simulator allows users to:
- Load historical U.S. Treasury yield curves (from FRED)
- Apply three canonical deformations: **parallel shift**, **steepening/flattening**, and **butterfly twist**
- Analyze the impact on a hypothetical coupon bond (price, Macaulay & modified duration)
- Visualize the **Principal Component Analysis (PCA)** of yield curve movements over the past 5 years

Ideal for economics olympiad preparation, university applications (PPE/Political Economy), or personal finance education.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- A free [FRED API key](https://fred.stlouisfed.org/docs/api/api_key.html)

### Installation
1. Clone or download this repository
2. Create a `.env` file in the root directory:
   ```env
   FRED_API_KEY=your_api_key_here
Open your browser at: http://localhost:8501

## 🧠 Key Features
- Feature     Compare yield curves during crises (2008, 2020) vs. normal periods
- Economic Insight     Quantify interest rate risk using duration theory
- Historical Scenarios     PCA Decomposition
- Bond Impact Analysis       Validate Litterman & Scheinkman (1991): 3 factors explain >90% of variance

## 📚 Academic Context
- Theory: Based on fixed income frameworks from Fabozzi, Tuckman, and CFA curriculum
- Data: Federal Reserve Economic Data (FRED) — official U.S. Treasury yields
- Tools: Python (NumPy, SciPy, scikit-learn), Streamlit for interactive UI
- Purpose: Bridge economic theory and data science for PPE/Political Economy application

## 📁 Project Structure
- yield_curve_simulator.py   # Main application with 3 tabs: Simulator, Bond, PCA
- requirements.txt           # Exact package versions
- screenshots/               # Demo images for README

## 🌐 Data Source
- FRED Series: DGS1MO, DGS3MO, DGS1, DGS2, DGS3, DGS5, DGS7, DGS10, DGS20, DGS30
- Official site: https://fred.stlouisfed.org
### 🎓 About the Author
-  Developed by Belous Ivan a 10th-grade student at Letovo School with a focus on:

- All-Russian School Olympiad in Economics (ВсОШ)
- University applications in PPE and Political economy (Philosophy, Politics, and Economics)
- Independent research in macroeconomics and financial markets
