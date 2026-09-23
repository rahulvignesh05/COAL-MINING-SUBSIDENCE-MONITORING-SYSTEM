# ⛏️ AI-Enabled Real-Time Mine Subsidence Monitoring and Early Warning System

## 🏭 Smart Mine Sentinel

An AI-powered, low-cost, real-time mine subsidence monitoring and early warning system designed for underground coal mines in India.

The system combines **IoT sensors, wireless communication, Artificial Intelligence, satellite InSAR data, computer vision, and GIS-based visualization** to continuously monitor structural and environmental conditions and identify early signs of mine subsidence.

---

## 📌 Problem Statement

**SIH26025 – Development of an AI-enabled Low Cost Real Time Mine Subsidence Monitoring, Prediction and Early Warning System for Underground Coal Mines in India**

Underground coal mining can cause ground deformation and subsidence, creating risks to mine workers, nearby communities, infrastructure, agricultural land, and the environment.

Conventional monitoring methods often depend on periodic field surveys and manual observations. These approaches may not provide continuous real-time information or early warnings.

Our proposed system addresses this challenge through an integrated monitoring platform capable of collecting sensor data, analysing structural conditions, detecting anomalies, and providing early warnings.

---

## 🎯 Objectives

- Monitor mine structural conditions in real time.
- Detect abnormal ground movement and structural changes.
- Analyse vibration, tilt, displacement, temperature, and humidity.
- Detect cracks using camera-based image analysis.
- Integrate satellite-based deformation monitoring using InSAR.
- Apply Machine Learning for anomaly detection and risk prediction.
- Provide real-time visualization through a centralized dashboard.
- Generate early warnings for potentially hazardous conditions.
- Develop a low-cost and scalable monitoring architecture.

---

## 🚀 Key Features

### 📡 Real-Time IoT Monitoring
Collects data from multiple sensors installed around the monitoring zone.

### 📐 Structural Monitoring
Monitors parameters such as:

- Tilt
- Acceleration
- Vibration
- Surface displacement
- Load
- Temperature
- Humidity

### 📷 AI-Based Crack Detection
ESP32-CAM can capture images of structural surfaces for crack detection and monitoring of crack growth.

### 🛰️ Satellite InSAR Monitoring
Satellite-based deformation data can be integrated to analyse long-term ground movement and surface deformation.

### 🤖 AI-Based Anomaly Detection
Machine Learning models analyse sensor and environmental data to identify abnormal patterns and classify potential risk conditions.

### 🗺️ GIS-Based Visualization
Monitoring locations and deformation information can be visualized geographically for easier interpretation.

### 📊 Real-Time Dashboard
A web-based dashboard provides:

- Live sensor readings
- Vibration analysis
- Deformation information
- AI predictions
- Crack monitoring
- Risk status
- Warning alerts

### ⚠️ Early Warning System
The system can classify monitoring conditions into different risk levels and generate alerts when abnormal behaviour is detected.

---

## 🧠 System Architecture

```text
                    ┌─────────────────────┐
                    │   Mine Environment  │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
        IoT Sensors        ESP32-CAM       Satellite Data
             │                 │                 │
             │                 │                 │
             └─────────────────┼─────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Data Acquisition &  │
                    │ Preprocessing Layer │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Feature Extraction  │
                    │ & Data Fusion       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   AI / ML Models    │
                    │ Anomaly Detection   │
                    │ Risk Prediction     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ FastAPI Backend     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Web Dashboard       │
                    │ React / JavaScript  │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
        Visualization                  Early Warning
        & Analytics                       Alerts
