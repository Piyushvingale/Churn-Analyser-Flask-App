from app import app
from flask import render_template
from flask import Flask,request, url_for, redirect, render_template
import pickle
import numpy as np
from flask import request, redirect, url_for, Flask
from flask_uploads import UploadSet, configure_uploads, ALL, DATA
import os
import pandas as pd
from flask_table import Table, Col


@app.route("/")
def index():
    return render_template("index.html")


model=pickle.load(open('app/static/model/DecisionTree.pkl','rb'))
app.config['INITIAL_FILE_UPLOADS'] = 'app/static/project'

def read_data(file):
    if file.endswith('.csv'):
        return pd.read_csv(file)
    elif file.endswith('.xls') or file.endswith('.xlsx'):
        return pd.read_excel(file)


@app.route('/results',methods=['POST','GET'])
def results():

    if request.method == "POST":
            
        file_upload = request.files['file_upload']
        filename = file_upload.filename
        file_upload.save(os.path.join(app.config['INITIAL_FILE_UPLOADS'], 'initial_data.csv'))
        df = pd.DataFrame(read_data(os.path.join(app.config['INITIAL_FILE_UPLOADS'], 'initial_data.csv')))
        new_df = df.iloc[:,:81].copy()
        X1 = new_df.copy()
        W1 = new_df.copy()
        Y1 = new_df['churn']
        Z1 = new_df['mobile_number']
        A1 = new_df['total_rech_amt_data_8']
        B1 = df['avg_total_rech_amt_data_av67']
        C1 = df['arpu_8']
        D1 = df['avg_arpu_av67']
        W1.drop(['churn','mobile_number'], inplace=True, axis=1)
        pred = model.predict(W1)
        dict1 = {
            'Mobile No': Z1.astype(str),
            'avg_8': A1,
            'avg_rech': B1.astype(float),
            'Churn': pred,
            'arpu_gp': C1,
            'arpu_ap': D1
        }
        mobile_df = pd.DataFrame(data=dict1)
        temp_df = mobile_df.loc[mobile_df['Churn'] == 1].copy()
        result_df = temp_df.loc[temp_df['avg_rech'] >= 478].copy()
        result_df.reset_index()

        #Shape
        tot_cust = df.shape[0]

        #High value customer
        hvc = round((df.loc[df['avg_total_rech_amt_data_av67'] > 478].shape[0]/df.shape[0])*100,2)

        #Average revenue
        avg_rev = round(np.average(df['avg_total_rech_amt_data_av67']),2)

        #Average net recharge amt
        avg_rech = round(np.average(df['avg_vbc_3g_av67']),2)

        hvc_rev = round(np.average(df.loc[df['avg_total_rech_amt_data_av67'] > 478]['avg_total_rech_amt_data_av67']),2)

        hvc_rech = round(np.average(df.loc[df['avg_total_rech_amt_data_av67'] > 478]['avg_vbc_3g_av67']),2)

        arpu_gpc = round(np.average(X1.loc[X1['churn'] == 1]['avg_arpu_av67']),2)

        arpu_gpnc = round(np.average(X1.loc[X1['churn'] != 1]['avg_arpu_av67']),2)

        arpu_apc = round(np.average(X1.loc[X1['churn'] == 1]['arpu_8']),2)

        arpu_apnc = round(np.average(X1.loc[X1['churn'] != 1]['arpu_8']),2)


    return render_template('analyse.html', 
        result_df = result_df, 
        tot_cust = tot_cust,
        hvc = hvc,
        avg_rev = avg_rev,
        hvc_rev = hvc_rev,
        avg_rech = avg_rech,
        hvc_rech = hvc_rech,
        tot_churn = result_df.shape[0],
        arpu_gpc = arpu_gpc,
        arpu_apc = arpu_apc,
        arpu_gpnc = arpu_gpnc,
        arpu_apnc = arpu_apnc)
       

if __name__ == '__main__':
    app.run(debug=True)
