#!/usr/bin/python3
from threading import Timer

from flask import Flask, request, jsonify, render_template_string, send_from_directory
import os
import pandas as pd
from datetime import datetime
import re
import itertools
import webbrowser

app = Flask(__name__)

BASE_DIR = os.path.join(os.getcwd(), 'uploads')
os.makedirs(BASE_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Date Range Selector</title>
</head>
<body>
<h1>Step 1: Select Date Range</h1>
<label for="date1">Start Date:</label>
<input type="date" id="date1" onchange="updateText()">
<label for="date2">End Date:</label>
<input type="date" id="date2" onchange="updateText()">
<p>
    Run this query in JIRA: <span style="color: green; font-weight: bold;" id="output"></span>
</p>
<p>And download the CSV file from JIRA</p>

<h1>Step 2: Upload CSV file downloaded from JIRA</h1>
<form action="/upload" method="post" enctype="multipart/form-data">
    <label for="file">Choose file:</label>
    <input type="file" id="file" name="file"><br>
    <input type="hidden" id="text" name="text"><br>
    <input type="submit" value="Process">
</form>

<script>
    function setDateToToday() {
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('date1').value = today;
        document.getElementById('date2').value = today;
        updateText(); // Update text initially with today's date
    }

    function updateText() {
        const date1 = document.getElementById('date1').value.replace(/-/g, '/');
        const date2 = document.getElementById('date2').value.replace(/-/g, '/');
        const text = `project = 'AS&E Desktop Support' and updatedDate >= '${date1}' and updatedDate <= '${date2}'`;
        document.getElementById('output').textContent = text
        document.getElementById('text').value = text
    }

    window.onload = setDateToToday; // Set today's date when the document loads
</script>
</body>
</html>
    """)

@app.route('/download/<filename>')
def download_file(filename):
    # Ensure the file is in the current directory for security
    return send_from_directory(BASE_DIR, filename, as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']

    # If the user does not select a file, the browser submits an empty part without filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Check if the text part is in the request
    if 'text' not in request.form:
        return jsonify({"error": "No text provided"}), 400
    text = request.form['text']

    if file:
        # Save the uploaded file to a temporary location to read with pandas
        filepath = os.path.join(BASE_DIR, file.filename)
        file.save(filepath)

        output_filename = process_data(text, filepath)

        # Return the path of the created Excel file
        return render_template_string("""
            <html>
            <body>
                <h1>Job Successful</h1>
                <a href="/download/{{ filename }}">Download file</a>
                <br><br>
                <hr>
                <a href="/">Process Again</a>
            </body>
            </html>
        """, filename=output_filename)

def process_data(query, filepath):

    import warnings
    warnings.filterwarnings('ignore')

    # Regex to match dates in the format 'YYYY/MM/DD'
    date_pattern = r"\d{4}/\d{2}/\d{2}"

    # Find all occurrences of the date pattern
    dates = re.findall(date_pattern, query)

    if dates:
        pulled_date_period= f"{dates[0]} - {dates[1]}"
    else:
        pulled_date_period= "Date Capturing Error"

    # raw_df = pd.read_csv('UR Service Management (JIRA) 2024-04-20T17_28_06-0400.csv')
    raw_df = pd.read_csv(filepath)

    desired_columns = ['Issue key'] + [col for col in raw_df.columns if col.startswith('Comment')]
    subset_df = raw_df[desired_columns] # Only the columns that we care about!

    for col in subset_df.columns: #Replace Comments with Usernames
        if col.startswith('Comment'):
            subset_df[col] = subset_df[col].str.extract(r';([^;]+);')


    # Below Code is intended to create Username lists for each issue/ticket and adding that as another colum ("Username")

    # Create an empty list to store usernames
    usernames_list = []

    # Iterate over each row in the DataFrame
    for index, row in subset_df.iterrows():
        # Create an empty list to store usernames in the current row
        row_usernames = []

         # Iterate over each comment column
        for col in subset_df.columns:
            if col.startswith('Comment'):
                # Check if the value is not NaN and add it to the list of usernames
                if not pd.isna(row[col]):
                    row_usernames.append(row[col])
                distinct_row_usernames = list(set(row_usernames))

        # Append the list of usernames for the current row to the main list
        usernames_list.append(distinct_row_usernames)

    subset_df.loc[:, 'Usernames'] = usernames_list

    for index, username in enumerate(usernames_list):
        print(f"Index: {index}, Username: {username}")

    filtered_df = subset_df[subset_df['Usernames'].apply(len) > 0] #Removing Tickets no-one commented on.

    listed_cp = []

    for index, row in filtered_df.iterrows(): #Creates the Cartesian Product
        x = list(itertools.product([row['Issue key']], row['Usernames']))
        listed_cp.append(x) # List of list of tuples

    unpacked_data = [item for sublist in listed_cp for item in sublist] #Unpaced to list of tuples

    export_df = pd.DataFrame(unpacked_data, columns=['Issue Key', 'Username'])

    export_df.insert(0, 'TimePeriod', pulled_date_period) #Inserts Time Period information retreived from Query

    username_count = export_df.groupby('Username').size().reset_index(name='Tickets Commented on')
    username_count = username_count.sort_values(by='Tickets Commented on', ascending=False)
    username_count.insert(0, 'TimePeriod', pulled_date_period)
    
    output_filename = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    output_filepath = os.path.join(BASE_DIR, output_filename)

    with pd.ExcelWriter(output_filepath) as writer:
        export_df.to_excel(writer, sheet_name='Raw Data', index=False)
        username_count.to_excel(writer, sheet_name='Aggregated Data', index=False)

    return output_filename


def open_browser():
    webbrowser.open_new('http://127.0.0.1:8000/')

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(host='0.0.0.0', port=8000, debug=False)
