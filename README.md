# RecSys: Recommendation System Project
This repository contains a recommendation system project implemented using collaborative filtering techniques.
## Project Overview
This project aims to develop a recommendation system using collaborative filtering methods. The system is designed to provide personalized recommendations based on user preferences and item similarities.
## Features
* Collaborative Filtering: Implements both user-based and item-based collaborative filtering algorithms.
* Data Preprocessing: Includes scripts for cleaning and preparing the input data.
* Evaluation Metrics: Incorporates various metrics to assess the performance of the recommendation system.
## Getting Started
### Prerequisites
* Python 3.7+
* pandas
* numpy
* scikit-learn
Installation
Clone the repository:
```bash
git clone https://github.com/Huvinesh-Rajendran-12/recsys.git
```

Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage
Prepare your data in the required format (CSV file with user, item, and rating columns).
Run the data preprocessing script:
```bash
python preprocess_data.py
```

Train the recommendation model:
```bash
python train_model.py
```

Generate recommendations:
```bash
python generate_recommendations.py
```
