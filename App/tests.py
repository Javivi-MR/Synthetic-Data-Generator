import unittest
import os
import time
import requests
from app import app, db
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

#Run this file when the server is running (python main.py) and the database is empty

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        with app.app_context():
            from models import User, Dataset

            datasets = Dataset.query.all()
            for dataset in datasets:
                db.session.delete(dataset)

            users = User.query.all()
            for user in users:
                db.session.delete(user)

            db.session.commit()

    def test_unit(self):
        from models import User, Dataset
        from utils import build_system, get_regression_line, load_dataset, authenticate_user
        from app import bcrypt

        build_system()

        with app.app_context():
            user = User(username='test', password=bcrypt.generate_password_hash('test'))
            db.session.add(user)
            db.session.commit()
            dataset = Dataset(name='test', path='test', user_id=1)
            db.session.add(dataset)
            db.session.commit()

            authenticated_user = authenticate_user('test', 'test')
            loaded_dataset = load_dataset(1)

        self.assertEqual(authenticated_user.username, 'test')
        self.assertTrue(bcrypt.check_password_hash(authenticated_user.password, 'test'))

        self.assertEqual(loaded_dataset.name, 'test')
        self.assertEqual(loaded_dataset.path, 'test')
        self.assertEqual(loaded_dataset.user_id, 1)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)
        examples_dir = os.path.join(root_dir, 'examples')
        iris = pd.read_csv(os.path.join(examples_dir, 'iris.csv'))

        self.assertEqual(round(iris['sepal_length'].mean(),2), 5.84)
        self.assertEqual(round(iris['sepal_length'].std(),2), 0.83)
        self.assertEqual(round(iris['sepal_width'].mean(),2), 3.05)
        self.assertEqual(round(iris['sepal_width'].std(),2), 0.43)
        self.assertEqual(round(iris['petal_length'].mean(),2), 3.76)
        self.assertEqual(round(iris['petal_length'].std(),2), 1.76)
        self.assertEqual(round(iris['petal_width'].mean(),2), 1.20)
        self.assertEqual(round(iris['petal_width'].std(),2), 0.76)

        self.assertEqual(round(iris['sepal_length'].corr(iris['sepal_width']),2), -0.11)
        self.assertEqual(round(iris['sepal_length'].corr(iris['petal_length']),2), 0.87)
        self.assertEqual(round(iris['sepal_length'].corr(iris['petal_width']),2), 0.82)
        self.assertEqual(round(iris['sepal_width'].corr(iris['petal_length']),2), -0.42)
        self.assertEqual(round(iris['sepal_width'].corr(iris['petal_width']),2), -0.36)
        self.assertEqual(round(iris['petal_length'].corr(iris['petal_width']),2), 0.96)

        self.assertEqual(round(iris['sepal_length'].cov(iris['sepal_width']),2), -0.04)

        x = iris['sepal_length']
        y = iris['sepal_width']
        slope, intercept = get_regression_line(x, y)
        self.assertEqual(round((iris['sepal_width'].mean() - (iris['sepal_length'].cov(iris['sepal_width']) / (iris['sepal_length'].std()**2) * iris['sepal_length'].mean())),2), round(intercept,2))
        self.assertEqual(round((iris['sepal_length'].cov(iris['sepal_width']) / iris['sepal_length'].std() ** 2),2), round(slope,2))




    def test_1_home_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Home', response.data)

    def test_2_register_page(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.maximize_window()

        driver.get('http://localhost:5000/register')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'submit')
        driver.execute_script("arguments[0].click();", submit)
        with app.app_context():
            from models import User
            user = User.query.filter_by(username='test').first()
            self.assertIsNotNone(user)
        driver.close()

    def test_3_login_page(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.maximize_window()


        driver.get('http://localhost:5000/register')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'submit')
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/login')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'loginb')
        driver.execute_script("arguments[0].click();", submit)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'Logout'))
        )
        driver.close()


    def test_4_logout_page(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.maximize_window()

        driver.get('http://localhost:5000/register')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'submit')
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/login')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'loginb')
        driver.execute_script("arguments[0].click();", submit)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'Logout'))
        )

        logout = driver.find_element(By.ID, 'Logout')
        driver.execute_script("arguments[0].click();", logout)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'Login'))
        )
        driver.close()

    def test_5_about_page(self):
        response = self.app.get('/about', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'About', response.data)

    def test_6_generate_page(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.maximize_window()

        driver.get('http://localhost:5000/generate')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'Login'))
        )

        driver.get('http://localhost:5000/register')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'submit')
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/login')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'loginb')
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/generate')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'upload'))
        )
        driver.close()

    def test_7_upload_dataset(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.maximize_window()

        driver.get('http://localhost:5000/register')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'submit')
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/login')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'loginb')
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/generate')
        upload = driver.find_element(By.ID, 'upload')
        driver.execute_script("arguments[0].click();", upload)

        dataset = driver.find_element(By.ID, 'dataset')
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)
        examples_dir = os.path.join(root_dir, 'examples')
        dataset.send_keys(os.path.join(examples_dir, 'iris.csv'))

        submit = driver.find_element(By.ID, 'submit')
        driver.execute_script("arguments[0].click();", submit)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'form_container_1'))
        )

        driver.close()

    def test_8_delete_dataset(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.maximize_window()

        driver.get('http://localhost:5000/register')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'submit')
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/login')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'loginb')
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/generate')
        upload = driver.find_element(By.ID, 'upload')
        driver.execute_script("arguments[0].click();", upload)

        dataset = driver.find_element(By.ID, 'dataset')
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)
        examples_dir = os.path.join(root_dir, 'examples')
        dataset.send_keys(os.path.join(examples_dir, 'iris.csv'))

        submit = driver.find_element(By.ID, 'submit')
        driver.execute_script("arguments[0].click();", submit)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'form_container_1'))
        )

        delete = driver.find_element(By.ID, 'delete_1')
        driver.execute_script("arguments[0].click();", delete)

        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.ID, 'form_container_1'))
        )

        driver.close()

    def test_9_generate_dataset(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.maximize_window()

        driver.get('http://localhost:5000/register')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'submit')
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/login')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'loginb')
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/generate')
        upload = driver.find_element(By.ID, 'upload')
        driver.execute_script("arguments[0].click();", upload)

        dataset = driver.find_element(By.ID, 'dataset')
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)
        examples_dir = os.path.join(root_dir, 'examples')
        dataset.send_keys(os.path.join(examples_dir, 'iris.csv'))

        submit = driver.find_element(By.ID, 'submit')
        driver.execute_script("arguments[0].click();", submit)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'form_container_1'))
        )

        ### FAST_ML ###
        rows = driver.find_element(By.ID, 'rows_1')
        rows.send_keys('150')
        synthetizer = driver.find_element(By.ID, 'synthetizer_1')
        synthetizer.send_keys('fast_ml')

        generate = driver.find_element(By.ID, 'GenButton_1')
        driver.execute_script("arguments[0].scrollIntoView();", generate)
        driver.execute_script("arguments[0].click();", generate)

        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.ID, 'SyntheticDataset'))
        )

        driver.get('http://localhost:5000/generate')

        ### gaussian_copula ###
        rows = driver.find_element(By.ID, 'rows_1')
        rows.send_keys('150')
        synthetizer = driver.find_element(By.ID, 'synthetizer_1')
        synthetizer.send_keys('gaussian_copula')

        generate = driver.find_element(By.ID, 'GenButton_1')
        driver.execute_script("arguments[0].scrollIntoView();", generate)
        driver.execute_script("arguments[0].click();", generate)

        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.ID, 'SyntheticDataset'))
        )

        driver.get('http://localhost:5000/generate')

        ### ctgan ###
        rows = driver.find_element(By.ID, 'rows_1')
        rows.send_keys('150')
        synthetizer = driver.find_element(By.ID, 'synthetizer_1')
        synthetizer.send_keys('ctgan')
        epochs = driver.find_element(By.ID, 'epochs_1')
        epochs.clear()
        epochs.send_keys('10')

        generate = driver.find_element(By.ID, 'GenButton_1')
        driver.execute_script("arguments[0].scrollIntoView();", generate)
        driver.execute_script("arguments[0].click();", generate)

        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.ID, 'SyntheticDataset'))
        )

        driver.get('http://localhost:5000/generate')

        ### copulagan ###
        rows = driver.find_element(By.ID, 'rows_1')
        rows.send_keys('150')
        synthetizer = driver.find_element(By.ID, 'synthetizer_1')
        synthetizer.send_keys('copulagan')
        epochs = driver.find_element(By.ID, 'epochs_1')
        epochs.clear()
        epochs.send_keys('10')

        generate = driver.find_element(By.ID, 'GenButton_1')
        driver.execute_script("arguments[0].scrollIntoView();", generate)
        driver.execute_script("arguments[0].click();", generate)

        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.ID, 'SyntheticDataset'))
        )

        driver.get('http://localhost:5000/generate')

        ### tvae ###
        rows = driver.find_element(By.ID, 'rows_1')
        rows.send_keys('150')
        synthetizer = driver.find_element(By.ID, 'synthetizer_1')
        synthetizer.send_keys('tvae')
        epochs = driver.find_element(By.ID, 'epochs_1')
        epochs.clear()
        epochs.send_keys('10')

        generate = driver.find_element(By.ID, 'GenButton_1')
        driver.execute_script("arguments[0].scrollIntoView();", generate)
        driver.execute_script("arguments[0].click();", generate)

        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.ID, 'SyntheticDataset'))
        )

        driver.close()

    def test_10_download_dataset(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.maximize_window()

        driver.get('http://localhost:5000/register')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'submit')
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/login')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'loginb')
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/generate')

        upload = driver.find_element(By.ID, 'upload')
        driver.execute_script("arguments[0].click();", upload)

        dataset = driver.find_element(By.ID, 'dataset')
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)
        examples_dir = os.path.join(root_dir, 'examples')
        dataset.send_keys(os.path.join(examples_dir, 'iris.csv'))

        submit = driver.find_element(By.ID, 'submit')
        driver.execute_script("arguments[0].click();", submit)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'form_container_1'))
        )

        ### FAST_ML ###
        rows = driver.find_element(By.ID, 'rows_1')
        rows.send_keys('150')
        synthetizer = driver.find_element(By.ID, 'synthetizer_1')
        synthetizer.send_keys('fast_ml')

        generate = driver.find_element(By.ID, 'GenButton_1')
        driver.execute_script("arguments[0].scrollIntoView();", generate)
        driver.execute_script("arguments[0].click();", generate)

        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.ID, 'SyntheticDataset'))
        )

        download = driver.find_element(By.ID, 'download_data')

        download_link = download.get_attribute('href')

        response = requests.get(download_link)

        self.assertEqual(response.status_code, 200)

        driver.close()

    def test_11_evaluate_page(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.maximize_window()

        driver.get('http://localhost:5000/register')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'submit')
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/login')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'loginb')
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/generate')
        upload = driver.find_element(By.ID, 'upload')
        driver.execute_script("arguments[0].click();", upload)

        dataset = driver.find_element(By.ID, 'dataset')
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)
        examples_dir = os.path.join(root_dir, 'examples')
        dataset.send_keys(os.path.join(examples_dir, 'iris.csv'))

        submit = driver.find_element(By.ID, 'submit')
        driver.execute_script("arguments[0].click();", submit)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'form_container_1'))
        )

        ### FAST_ML ###
        rows = driver.find_element(By.ID, 'rows_1')
        rows.send_keys('150')
        synthetizer = driver.find_element(By.ID, 'synthetizer_1')
        synthetizer.send_keys('fast_ml')

        generate = driver.find_element(By.ID, 'GenButton_1')
        driver.execute_script("arguments[0].scrollIntoView();", generate)
        driver.execute_script("arguments[0].click();", generate)

        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.ID, 'SyntheticDataset'))
        )

        evaluate = driver.find_element(By.ID, 'EvButton')
        driver.execute_script("arguments[0].click();", evaluate)

        WebDriverWait(driver, 35).until(
            EC.presence_of_element_located((By.ID, 'QualityHeader'))
        )

        driver.close()

if __name__ == '__main__':
    unittest.main()