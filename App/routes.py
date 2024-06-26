from flask import render_template, url_for, request, redirect
from app import app, db
from models import User, Dataset
from forms import Register, Login
from utils import build_system, load_dataset, authenticate_user, has_header, separate_with_comma
from flask_login import login_user, login_required, logout_user, current_user
import pandas as pd
import numpy as np
import os
import warnings
import matplotlib.pyplot as plt
from sdv.lite import SingleTablePreset
from sdv.metadata import SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer, CTGANSynthesizer, CopulaGANSynthesizer, TVAESynthesizer
from sdmetrics.reports.single_table import QualityReport
from sdmetrics.visualization import get_column_plot
import config as C

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html', user=current_user)

@app.route('/login', methods=['POST', 'GET'])
def login():
    loginform = Login()
    # if the form is submitted
    if loginform.validate_on_submit():
        # check if the user exists
        user = authenticate_user(loginform.username.data, loginform.password.data)
        if user:
            # login the user
            login_user(user)
            return redirect(url_for('index'))
        return render_template('error.html', user=current_user, error='Invalid username or password')
    return render_template('login.html', form=loginform, user=current_user, p='')

@app.route('/forgot', methods=['POST', 'GET'])
def forgot():
    return render_template('forgot.html', user=current_user)

@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    from app import bcrypt
    registerform = Register()

    # if the form is submitted
    if registerform.validate_on_submit():
        # hash the password
        hashed_password = bcrypt.generate_password_hash(registerform.password.data)
        # create the user
        user = User(username=registerform.username.data, password=hashed_password)
        # add the user to the database
        db.session.add(user)
        db.session.commit()
        return render_template('login.html', user=current_user, form=Login() , p='User created successfully, now you can login.')
    elif registerform.errors:
        return render_template('error.html', user=current_user, error='Username already exists. Choose a different one.')


    return render_template('register.html', form=registerform, user=current_user)


@app.route('/generate', methods=['POST', 'GET'])
@login_required
def generate():
    # get the references to the datasets of the user
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    # list to store the datasets as pandas dataframes objects
    datasets_objs = []
    for dataset in datasets:
        datasets_objs.append(pd.read_csv(dataset.path))
    return render_template('generate.html',user=current_user, datasets=datasets, datasets_objs=datasets_objs)

@app.route('/generate/<id>', methods=['POST', 'GET'])
@login_required
def generate_id(id):
    if request.method == 'POST':
        warnings.simplefilter(action='ignore', category=FutureWarning)

        # check if the number of rows and epochs are greater than 0
        if int(request.form['rows_' + str(id)]) <= 0 or int(request.form['epochs_' + str(id)]) <= 0:
            return render_template('error.html', user=current_user, error='The number of rows and epochs must be greater than 0')

        # dictionary to parse the yes/no values from the form
        yes_no_parser = {'Yes': True, 'No': False}

        # load the dataset
        dataset = load_dataset(id)
        # check if the dataset exists and if it belongs to the user
        if dataset is None or dataset.user_id != current_user.id or not os.path.exists(dataset.path):
            # redirect to the generate page if the dataset does not exist or does not belong to the user
            return redirect(url_for('generate'))
        real_data = pd.read_csv(dataset.path)

        v_metadata = SingleTableMetadata()
        v_metadata.detect_from_dataframe(real_data)
        synthetic_data = None

        # Fast ML synthesizer
        if request.form['synthetizer_' + str(id)] == 'fast_ml':
            synthesizer = SingleTablePreset(v_metadata, name='FAST_ML')
            synthesizer.fit(real_data)
            synthetic_data = synthesizer.sample(int(request.form['rows_' + str(id)]))

        # CopulaGAN synthesizer
        elif request.form['synthetizer_' + str(id)] == 'copulagan':
            v_enforce_min_max = yes_no_parser[request.form['enforce_min_max_values_' + str(id)]]

            v_enforce_rounding = yes_no_parser[request.form['enforce_rounding_' + str(id)]]

            v_epochs = int(request.form['epochs_' + str(id)])

            columns_distribution = {}

            v_cuda = yes_no_parser[request.form['cuda_' + str(id)]]

            for column in real_data.columns:
                if request.form[column + '_' + str(id)] != 'none':
                    columns_distribution[column] = request.form[column + '_' + str(id)]

            if not columns_distribution:
                columns_distribution = None

            v_default_distribution = request.form['default_distribution_' + str(id)]

            synthesizer = CopulaGANSynthesizer(
                metadata=v_metadata,
                enforce_min_max_values=v_enforce_min_max,
                enforce_rounding=v_enforce_rounding,
                numerical_distributions=columns_distribution,
                default_distribution=v_default_distribution,
                epochs=v_epochs,
                verbose=True,
                cuda=v_cuda)

            synthesizer.fit(real_data)
            synthetic_data = synthesizer.sample(int(request.form['rows_' + str(id)]))

        # CTGAN synthesizer
        elif request.form['synthetizer_' + str(id)] == 'ctgan':
            v_enforce_min_max = yes_no_parser[request.form['enforce_min_max_values_' + str(id)]]

            v_enforce_rounding = yes_no_parser[request.form['enforce_rounding_' + str(id)]]

            v_epochs = int(request.form['epochs_' + str(id)])

            v_cuda = yes_no_parser[request.form['cuda_' + str(id)]]

            synthesizer = CTGANSynthesizer(
                metadata=v_metadata,
                enforce_min_max_values=v_enforce_min_max,
                enforce_rounding=v_enforce_rounding,
                epochs=v_epochs,
                verbose=True,
                cuda=v_cuda
            )

            synthesizer.fit(real_data)
            synthetic_data = synthesizer.sample(int(request.form['rows_' + str(id)]))

        # Gaussian Copula synthesizer
        elif request.form['synthetizer_' + str(id)] == 'gaussian_copula':
            v_enforce_min_max = yes_no_parser[request.form['enforce_min_max_values_' + str(id)]]

            v_enforce_rounding = yes_no_parser[request.form['enforce_rounding_' + str(id)]]

            columns_distribution = {}

            for column in real_data.columns:
                if request.form[column + '_' + str(id)] != 'none':
                    columns_distribution[column] = request.form[column + '_' + str(id)]

            if not columns_distribution:
                columns_distribution = None

            v_default_distribution = request.form['default_distribution_' + str(id)]

            synthesizer = GaussianCopulaSynthesizer(
                metadata=v_metadata,
                enforce_min_max_values=v_enforce_min_max,
                enforce_rounding=v_enforce_rounding,
                numerical_distributions=columns_distribution,
                default_distribution=v_default_distribution
            )
            synthesizer.fit(real_data)
            synthetic_data = synthesizer.sample(int(request.form['rows_' + str(id)]))

        # TVAE synthesizer
        elif request.form['synthetizer_' + str(id)] == 'tvae':
            v_enforce_min_max = yes_no_parser[request.form['enforce_min_max_values_' + str(id)]]

            v_enforce_rounding = yes_no_parser[request.form['enforce_rounding_' + str(id)]]

            v_epochs = int(request.form['epochs_' + str(id)])

            v_cuda = yes_no_parser[request.form['cuda_' + str(id)]]

            synthesizer = TVAESynthesizer(
                metadata=v_metadata,
                enforce_min_max_values=v_enforce_min_max,
                enforce_rounding=v_enforce_rounding,
                epochs=v_epochs,
                cuda=v_cuda
            )

            # train the synthesizer with the real data
            synthesizer.fit(real_data)
            # generate synthetic data with the number of rows specified by the user
            synthetic_data = synthesizer.sample(int(request.form['rows_' + str(id)]))
        else:
            return render_template('error.html', user=current_user, error='Invalid synthetizer')

        # save the synthetic data to a csv file
        synthetic_data.to_csv(os.path.join(app.root_path,C.SYNTHETIC_PATH + str(id) + '_s_' + dataset.name), index=False)
        return render_template('showdata.html', id=id, user=current_user ,file_name=dataset.name, real_data=real_data, synthetic_data=synthetic_data, C_SYNTHETIC_PATH=C.SYNTHETIC_PATH, C_PLOT_PATH=C.PLOT_PATH)
    else:
        return redirect(url_for('generate'))


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'dataset' not in request.files:
            return render_template('error.html', user=current_user, error='No selected file.')

        file = request.files['dataset']

        # check if the file is empty
        if file.filename == '':
            return render_template('error.html', user=current_user, error='No selected file.')

        # check if the file is a csv file
        if file.filename.split('.')[-1] != 'csv':
            return render_template('error.html', user=current_user, error='The file must be a csv file.')

        # check if the csv uploaded has headers
        if not has_header(file):
            return render_template('error.html', user=current_user, error='The file must have headers.')

        # check if the csv uploaded is separated by commas
        if not separate_with_comma(file):
            return render_template('error.html', user=current_user, error='The file must be separated by commas.')

        # check if the headers contain special characters
        header_line = file.readline().decode('utf-8').strip()
        if not all(c.isalnum() or c == '.' or c == '-' or c == ':' or c == ',' or c == '_' for c in header_line):
            return render_template('error.html', user=current_user,
                                   error='The headers must not contain special characters.')

        # position the file pointer at the beginning of the file
        file.seek(0)

        # get the last dataset id
        last_dataset = db.session.query(Dataset).order_by(Dataset.id.desc()).first()

        # Check if a dataset was returned
        if last_dataset is not None:
            id = last_dataset.id + 1
        else:
            id = 1

        # save the file
        file.save(os.path.join(app.root_path, C.DATASET_PATH + str(id) + '_' + file.filename))
        dataset = Dataset(id=id, name=file.filename, path=os.path.join(app.root_path, C.DATASET_PATH + str(id) + '_' + file.filename), user_id=current_user.id)
        db.session.add(dataset)
        db.session.commit()

        return redirect(url_for('generate'))

    else:
        return render_template('upload.html', user=current_user)

@app.route('/delete/<id>', methods=['POST', 'GET'])
@login_required
def delete(id):
    if request.method == 'POST':
        # get the dataset information
        dataset = load_dataset(id)
        # check if the dataset exists and if it belongs to the user
        if dataset is None or dataset.user_id != current_user.id:
            return redirect(url_for('generate'))

        # delete the dataset from the database
        db.session.delete(dataset)
        db.session.commit()

        # delete the file
        os.remove(dataset.path)
        return redirect(url_for('generate'))
    else:
        return redirect(url_for('generate'))

@app.route('/evaluate/<id>', methods=['POST', 'GET'])
@login_required
def evaluate(id):
    from utils import get_regression_line

    # check if the dataset exists and if it belongs to the user
    dataset = load_dataset(id)
    if dataset is None or dataset.user_id != current_user.id or not os.path.exists(dataset.path) or not os.path.exists(os.path.join(app.root_path,C.SYNTHETIC_PATH + str(id) + '_s_' + dataset.name)):
        return redirect(url_for('generate'))

    # load the real and synthetic data as pandas dataframes
    real_data = pd.read_csv(dataset.path)
    synthetic_data = pd.read_csv(os.path.join(app.root_path,C.SYNTHETIC_PATH + str(id) + '_s_' + dataset.name))
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(real_data)

    # Generate the quality report
    report = QualityReport()
    report.generate(real_data, synthetic_data,metadata.to_dict())

    # Save the plot of columns similarities
    column_fig = report.get_visualization(property_name='Column Shapes')
    column_fig.write_image(os.path.join(app.root_path,C.PLOT_PATH + str(id) + 'column_shapes.png'))

    # Save the plot of columns pairs trends
    pair_fig = report.get_visualization(property_name='Column Pair Trends')
    pair_fig.write_image(os.path.join(app.root_path, C.PLOT_PATH + str(id) + 'column_pair_trends.png'))

    # Save the plot of columns distributions
    for column in real_data.columns:
        plot = get_column_plot(real_data, synthetic_data, column)
        plot.write_image(os.path.join(app.root_path,C.PLOT_PATH + str(id) + column + '.png'))

    # Save the pairs of numerical columns
    num_columns = len(real_data.columns)
    column_pairs = [(real_data.columns[i], real_data.columns[j])
                    for i in range(num_columns)
                    for j in range(i + 1, num_columns)
                    if real_data[real_data.columns[i]].dtype in ['int64', 'float64'] and
                    real_data[real_data.columns[j]].dtype in ['int64', 'float64']]

    # pair plots covariance
    for column1, column2 in column_pairs:
        plt.figure(figsize=(10, 6))
        plt.scatter(real_data[column1], real_data[column2], color='blue', alpha=0.5, label='Real Data')
        plt.scatter(synthetic_data[column1], synthetic_data[column2], color='red', alpha=0.5, label='Synthetic Data')
        plt.xlabel(column1)
        plt.ylabel(column2)
        plt.legend()
        plt.savefig(os.path.join(app.root_path, C.PLOT_PATH + str(id) + column1 + column2 + '.png'))
        plt.close()

    # pair plots regression
    for column1, column2 in column_pairs:
        plt.figure(figsize=(10, 6))
        plt.scatter(real_data[column1], real_data[column2], color='blue', alpha=0.5, label='Real Data')
        plt.scatter(synthetic_data[column1], synthetic_data[column2], color='red', alpha=0.5, label='Synthetic Data')
        slope, intercept = get_regression_line(real_data[column1], real_data[column2])
        plt.plot(real_data[column1], slope * real_data[column1] + intercept, color='blue')
        slope, intercept = get_regression_line(synthetic_data[column1], synthetic_data[column2])
        plt.plot(synthetic_data[column1], slope * synthetic_data[column1] + intercept, color='red')
        plt.xlabel(column1)
        plt.ylabel(column2)
        plt.legend()
        plt.savefig(os.path.join(app.root_path,C.PLOT_PATH + str(id) + column1 + column2 + 'reg' + '.png'))
        plt.close()

    return render_template('evaluate.html',user=current_user,file_name=dataset.name,id=id,score=report.get_score(),real_data=real_data,synthetic_data=synthetic_data, column_pairs=column_pairs, C_PLOT_PATH=C.PLOT_PATH, C_SYNTHETIC_PATH=C.SYNTHETIC_PATH)

@app.route('/about', methods=['POST', 'GET'])
def about():
    return render_template('about.html' , user=current_user)