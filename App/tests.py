import unittest
import os
import time
from app import app, db
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

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

    def test_1_home_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Home', response.data)

    def test_2_register_page(self):
        # Use selenium to fill and submit the register form
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
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)
        # Check if the user was created
        with app.app_context():
            from models import User
            user = User.query.filter_by(username='test').first()
            self.assertIsNotNone(user)
        driver.close()

    def test_3_login_page(self):
        # Use selenium to fill and submit the login form
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
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/login')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'loginb')
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        # Check if the user is logged in
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'Logout'))
        )
        driver.close()


    def test_4_logout_page(self):
        # Use selenium to fill and submit the login form
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
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/login')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'loginb')
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        # Check if the user is logged in
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'Logout'))
        )

        # Logout
        logout = driver.find_element(By.ID, 'Logout')
        #logout.click()
        driver.execute_script("arguments[0].click();", logout)

        # Check if the user is logged out
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

        #first check you can't access the page without being logged in
        driver.get('http://localhost:5000/generate')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'Login'))
        )

        #second check you can access the page after logging in
        driver.get('http://localhost:5000/register')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'submit')
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/login')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'loginb')
        #submit.click()
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
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/login')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'loginb')
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/generate')
        #search upload button
        upload = driver.find_element(By.ID, 'upload')
        #click it
        #upload.click()
        driver.execute_script("arguments[0].click();", upload)

        #form with a file input with id 'dataset' and a submit button with id 'submit'
        dataset = driver.find_element(By.ID, 'dataset')
        #attach the file at "../examples/iris.csv" use os.path.abspath to get the full path
        #dataset.send_keys(os.path.abspath('../examples/iris.csv'))
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
        file_path = os.path.join(script_dir, '../examples/iris.csv')  # Construct the path to the iris.csv file
        dataset.send_keys(file_path)
        submit = driver.find_element(By.ID, 'submit')
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        #Check if the dataset was uploaded
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
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/login')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'loginb')
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/generate')
        #search upload button
        upload = driver.find_element(By.ID, 'upload')
        #click it
        #upload.click()
        driver.execute_script("arguments[0].click();", upload)

        #form with a file input with id 'dataset' and a submit button with id 'submit'
        dataset = driver.find_element(By.ID, 'dataset')
        #attach the file at "../examples/iris.csv" use os.path.abspath to get the full path
        #dataset.send_keys(os.path.abspath('../examples/iris.csv'))
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
        file_path = os.path.join(script_dir, '../examples/iris.csv')  # Construct the path to the iris.csv file
        dataset.send_keys(file_path)
        submit = driver.find_element(By.ID, 'submit')
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        #Check if the dataset was uploaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'form_container_1'))
        )

        #search delete button
        delete = driver.find_element(By.ID, 'delete_1')
        #click it
        #delete.click()
        driver.execute_script("arguments[0].click();", delete)

        #Check if the dataset was deleted
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
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/login')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'loginb')
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/generate')
        # search upload button
        upload = driver.find_element(By.ID, 'upload')
        # click it
        #upload.click()
        driver.execute_script("arguments[0].click();", upload)

        # form with a file input with id 'dataset' and a submit button with id 'submit'
        dataset = driver.find_element(By.ID, 'dataset')
        # attach the file at "../examples/iris.csv" use os.path.abspath to get the full path
        #dataset.send_keys(os.path.abspath('../examples/iris.csv'))
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
        file_path = os.path.join(script_dir, '../examples/iris.csv')  # Construct the path to the iris.csv file
        dataset.send_keys(file_path)
        submit = driver.find_element(By.ID, 'submit')
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        # Check if the dataset was uploaded
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
        #generate.click()
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
        #generate.click()
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
        #generate.click()
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
        #generate.click()
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
        #generate.click()
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
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/login')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'loginb')
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/generate')
        # search upload button
        upload = driver.find_element(By.ID, 'upload')
        # click it
        #upload.click()
        driver.execute_script("arguments[0].click();", upload)

        # form with a file input with id 'dataset' and a submit button with id 'submit'
        dataset = driver.find_element(By.ID, 'dataset')
        # attach the file at "../examples/iris.csv" use os.path.abspath to get the full path
        #dataset.send_keys(os.path.abspath('../examples/iris.csv'))
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
        file_path = os.path.join(script_dir, '../examples/iris.csv')  # Construct the path to the iris.csv file
        dataset.send_keys(file_path)
        submit = driver.find_element(By.ID, 'submit')
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        # Check if the dataset was uploaded
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
        #generate.click()
        driver.execute_script("arguments[0].click();", generate)

        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.ID, 'SyntheticDataset'))
        )

        download = driver.find_element(By.ID, 'download_data')
        #download.click()
        driver.execute_script("arguments[0].click();", download)

        time.sleep(10)

        downloads_folder = os.path.expanduser("~\\Downloads")

        self.assertTrue(os.path.exists(os.path.join(downloads_folder, '1_s_iris.csv')), "Downloaded file does not exist")

        if os.path.exists(os.path.join(downloads_folder, '1_s_iris.csv')):
            os.remove(os.path.join(downloads_folder, '1_s_iris.csv'))

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
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/login')
        username = driver.find_element(By.ID, 'username')
        username.send_keys('test')
        password = driver.find_element(By.ID, 'password')
        password.send_keys('test')

        submit = driver.find_element(By.ID, 'loginb')
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        driver.get('http://localhost:5000/generate')
        # search upload button
        upload = driver.find_element(By.ID, 'upload')
        # click it
        #upload.click()
        driver.execute_script("arguments[0].click();", upload)

        # form with a file input with id 'dataset' and a submit button with id 'submit'
        dataset = driver.find_element(By.ID, 'dataset')
        # attach the file at "../examples/iris.csv" use os.path.abspath to get the full path
        #dataset.send_keys(os.path.abspath('../examples/iris.csv'))
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
        file_path = os.path.join(script_dir, '../examples/iris.csv')  # Construct the path to the iris.csv file
        dataset.send_keys(file_path)
        submit = driver.find_element(By.ID, 'submit')
        #submit.click()
        driver.execute_script("arguments[0].click();", submit)

        # Check if the dataset was uploaded
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
        #generate.click()
        driver.execute_script("arguments[0].click();", generate)

        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.ID, 'SyntheticDataset'))
        )

        evaluate = driver.find_element(By.ID, 'EvButton')
        #evaluate.click()
        driver.execute_script("arguments[0].click();", evaluate)

        WebDriverWait(driver, 35).until(
            EC.presence_of_element_located((By.ID, 'QualityHeader'))
        )

        driver.close()

if __name__ == '__main__':
    unittest.main()