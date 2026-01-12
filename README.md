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
