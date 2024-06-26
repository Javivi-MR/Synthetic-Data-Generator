# Synthetic-Data-Generator
This repository contains the source code of my Bachelor's Degree Final Project, featuring a Flask application that implements SDV (Synthetic Data Vault) for generating synthetic datasets from a given CSV dataset. Explore the codebase to leverage powerful data synthesis capabilities in your projects.

# Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
    - [Using Docker](#using-docker)
    - [Manually](#manually)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

# Introduction
SDV (Synthetic Data Vault) is a Python library that provides a set of tools for generating synthetic datasets.

The library is designed to be easy to use and flexible, allowing users to apply different synthesis techniques to different columns of a dataset, and to combine these techniques in a single model.

This repository contains a Flask application that implements SDV for generating synthetic datasets from a given CSV dataset.

# Installation
If you want to just test the application, without going through the installation process, a web version is available <a href="https://syntheticdatagen1.azurewebsites.net/">Here</a>. However, please note that this deployed version has limited resources. It is best suited for testing with smaller datasets, such as those with a few rows and columns. For example, the Iris dataset (5 columns and 150 rows) works well. This limitation ensures that the application remains responsive and accessible to all users. 

There are two ways to install the application: using Docker or manually.

## Using Docker
1. Install Docker on your machine. You can download it from the official website: https://www.docker.com/get-started
2. Clone this repository to your local machine.
3. Open a terminal and navigate to the root directory of the cloned repository.
4. Run the following command to build the Docker image:
```bash
docker compose up --build
```

## Manually
1. Clone this repository to your local machine.
2. Install Python 3.9 on your machine. You can download it from the official website: https://www.python.org/downloads/
3. Open a terminal and navigate to the root directory of the cloned repository.
4. Run the following command to create a virtual environment:
```bash
python -m venv venv
```
5. Run the following command to activate the virtual environment:
```bash
source venv/bin/activate
```
6. Run the following command to install the required packages:
```bash
pip install -r requirements.txt
```
7. Run the following command to start the Flask application:
```bash
flask run
```

# Usage
1. Open a web browser and navigate to localhost:50505 if you installed the application using Docker, or localhost:5000 if you installed it manually.

2. To generate a synthetic dataset, first you need to register an account. Click on the "Login" button in the top right corner of the page, then click on the "Don't have an account? Register here". Fill in the required information and click on the "Register" button.

3. Once you have registered an account, you can log in using your username and password.

4. After logging in, you will be redirected to the home page. Click on the "Generate" button to go to the dataset generation page.

5. On the dataset generation page, you can upload a CSV file containing the dataset you want to generate synthetic data for. The file should have a header row with column names and these must not contain any special characters or spaces except for underscores (_), periods (.), and hyphens(-). The separator should be a comma (,).

6. After uploading the file, you can select a number of rows to generate and the synthetizer to use. The available synthetizers are:
    - Fast ML
    - Gaussian Copula
    - CTGAN
    - CopulaGAN
    - TVAE
Each synthetizer has its own parameters that can be adjusted to customize the generation process.

7. Click on the "Generate" button to start the generation process. Once the process is complete, you will be redirected to a page where you can see a preview of the synthetic dataset, download it as a CSV file, or evaluate its quality.

8. To evaluate the quality of the synthetic dataset, you can use the "Evaluate" button. This will take you to a page where you can compare the original and synthetic datasets using various metrics such as:
    - Mean 
    - Standard Deviation
    - Mode
    - Covariance
    - Pearson Correlation
    - Regression Line
    - R2 Score

# Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions, questions, or feedback.

# License
This project is licensed under the GNU General Public License v3.0. See the LICENSE file for details.
```
