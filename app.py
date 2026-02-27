from flask import Flask, request, jsonify, render_template,make_response, Response, send_from_directory,send_file,flash
from app.forms import MyForm, LoadTestForm , RequestsForm
from app.models import TestResult,db
import requests
import time
from concurrent.futures import ThreadPoolExecutor
import subprocess
import json
import io
import pandas as pd
import matplotlib.pyplot as plt
import re
from reportlab.pdfgen import canvas
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import textwrap
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph, Spacer
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/osmanbatuhanural/Desktop/001142721_OSMAN_BATUHAN_URAL/SSU_LOAD_TESTING/instance/test_results.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db.init_app(app)
app.config['SECRET_KEY'] = '1111'

@app.route('/previous_scans')
def previous_scans():
    
    with app.app_context():
        
        test_results = TestResult.query.all()
        
        return render_template('previous_scans.html', test_results=test_results)


@app.route('/load-test', methods=['GET', 'POST'])
def load_test_endpoint():
    form = MyForm()  
    if request.method == 'POST':
        url = form.url.data
        num_requests = int(form.num_requests.data)
        test_results = perform_load_test(url, num_requests)
        details_for_storage = {key: test_results[key] for key in test_results if key != 'summary_message'}
        serialized_details = json.dumps(details_for_storage)
        
        new_test_result = TestResult(
            test_type='load-test',
            details=serialized_details,
            message=test_results['summary_message'],  
            url=url
        )
        db.session.add(new_test_result)
        db.session.commit()
        
        return jsonify(test_results)  

    return render_template('load_test.html', form=form)

def perform_load_test(url, num_requests):
    total_time = 0
    response_times = []
    statuses = []
    timeout_seconds = 5

    for i in range(num_requests):
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout_seconds)
            end_time = time.time()
            elapsed_time = end_time - start_time

            total_time += elapsed_time
            response_times.append(elapsed_time)
            statuses.append(response.status_code)

        except requests.exceptions.RequestException as e:
            statuses.append('Error')
            response_times.append(timeout_seconds)

    average_time = total_time / num_requests if num_requests > 0 else 0
    success_responses = statuses.count(200)
    success_percentage = (success_responses / num_requests) * 100 if num_requests > 0 else 0
    throughput = num_requests / total_time if total_time > 0 else 0

    results_with_higher_than_average = [
        {"Request Number": i + 1, "Status Code": statuses[i], "Response Time": response_times[i]}
        for i, resp_time in enumerate(response_times) if resp_time > average_time
    ]

    summary_message = (
        f"Load Test for {url}:\n"
        f"- Average Response Time: {average_time:.2f} seconds\n"
        f" \n The URL you have completed the test gives a response at {average_time:.2f} seconds on average. Response times of 0.1 seconds and less are considered instantaneous response and are considered to be the most ideal situation. Response times of 1 second and below are invisible to the user's experience and are quite acceptable. Messages between 1-10 seconds give the user a sense of delay and require improvement \n"
        f"-\n Requests Slower than Average: {len(results_with_higher_than_average)}\n"
        f" \n Your response count of {len(response_times)} includes {len(results_with_higher_than_average)} that are above the average response time. If you observe an anomaly, repeat the test, if it is continuous, it requires improvement.\n"
        f"-\n Success Rate: {success_percentage:.0f}%\n"
        f" \n  of the requests sent during the test were responded to by the server.\n"
        f"-\n Throughput: {throughput:.2f} requests per second\n"
        f" \n This score can be used to compare the performance of the URL being tested against other scenarios."
    )

    results = {
        "average_response_time": average_time,
        "number_of_requests_higher_than_average": len(results_with_higher_than_average),
        "details_of_requests_higher_than_average": results_with_higher_than_average,
        "success_percentage": success_percentage,
        "throughput": throughput,
        "summary_message": summary_message
    }

    return results



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/base')
def base():
    return render_template('base.html')


@app.route('/multi-load-test', methods=['GET', 'POST'])
def multi_load_test():
    form = LoadTestForm()  
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            urls = data['urls']
            num_requests = int(data['num_requests'])
        else:
            if form.validate_on_submit():
                urls = [url.strip() for url in form.urls.data if url.strip()]
                num_requests = int(form.num_requests.data)
        test_results_list = []

        for url in urls:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            test_results = perform_multi_load_test(url, num_requests)
            details_for_storage = {key: test_results[key] for key in test_results if key != 'summary_message'}
            serialized_details = json.dumps(details_for_storage)

            
            new_test_result = TestResult(
                test_type='multi-load-test',
                url=url,
                details=serialized_details,
                message=test_results['summary_message']
            )
            db.session.add(new_test_result)
            test_results_list.append(test_results)

        db.session.commit()

        return jsonify(test_results_list)

    return render_template('multiload_test.html', form=form)

def perform_multi_load_test(url, num_requests):
    total_time = 0
    response_times = []
    statuses = []
    timeout_seconds = 5

    for i in range(num_requests):
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout_seconds)
            end_time = time.time()
            elapsed_time = end_time - start_time

            total_time += elapsed_time
            response_times.append(elapsed_time)
            statuses.append(response.status_code)

        except requests.exceptions.RequestException as e:
            statuses.append('Error')
            response_times.append(timeout_seconds)

    average_time = total_time / num_requests if num_requests > 0 else 0
    success_responses = statuses.count(200)
    success_percentage = (success_responses / num_requests) * 100 if num_requests > 0 else 0

    
    throughput = success_responses / total_time if total_time > 0 else 0

    results_with_higher_than_average = [
        {"Request Number": i + 1, "Status Code": statuses[i], "Response Time": response_times[i]}
        for i, resp_time in enumerate(response_times) if resp_time > average_time
    ]

    summary_message = (
        f"Load Test for {url}:\n"
        f"- Average Response Time: {average_time:.2f} seconds\n"
        f" \n The URL you have completed the test gives a response at {average_time:.2f} seconds on average. Response times of 0.1 seconds and less are considered instantaneous response and are considered to be the most ideal situation. Response times of 1 second and below are invisible to the user's experience and are quite acceptable. Messages between 1-10 seconds give the user a sense of delay and require improvement \n"
        f"-\n Requests Slower than Average: {len(results_with_higher_than_average)}\n"
        f" \n Your response count of {len(response_times)} includes {len(results_with_higher_than_average)} that are above the average response time. If you observe an anomaly, repeat the test, if it is continuous, it requires improvement.\n"
        f"-\n Success Rate: {success_percentage:.0f}%\n"
        f" \n  of the requests sent during the test were responded to by the server.\n"
        f"-\n Throughput: {throughput:.2f} requests per second\n"
        f" \n This score can be used to compare the performance of the URL being tested against other scenarios."
    )

    return {
        "average_response_time": average_time,
        "number_of_requests_higher_than_average": len(results_with_higher_than_average),
        "details_of_requests_higher_than_average": results_with_higher_than_average,
        "success_percentage": success_percentage,
        "summary_message": summary_message,
        "throughput": throughput  
    }


def send_request_and_measure_time(url_user_pair):
    url, user_id = url_user_pair
    start_time = time.time()
    response = requests.get(url)
    end_time = time.time()
    return {
        "user_id": user_id,
        "response_time": end_time - start_time,
        "status_code": response.status_code
    }



def send_multiple_requests(website_url, num_users, num_requests_per_user):
    urls_with_user_id = [(website_url, user_id) for user_id in range(num_users) for _ in range(num_requests_per_user)]
    total_start_time = time.time()

    with ThreadPoolExecutor(max_workers=num_users) as executor:
        results = list(executor.map(send_request_and_measure_time, urls_with_user_id))

    total_end_time = time.time()
    total_time = total_end_time - total_start_time
    total_requests = num_users * num_requests_per_user
    throughput = total_requests / total_time if total_time > 0 else 0

    response_times = [result['response_time'] for result in results]
    average_response_time = sum(response_times) / len(response_times) if response_times else 0
    results_with_higher_than_average = [result for result in results if result['response_time'] > average_response_time]

    summary_message = (
        f"Load Test for {website_url}:\n"
        f"- Average Response Time: {average_response_time:.2f} seconds\n"
        f" \n The URL you have completed the test gives a response at {average_response_time:.2f} seconds on average. Response times of 0.1 seconds and less are considered instantaneous response and are considered to be the most ideal situation. Response times of 1 second and below are invisible to the user's experience and are quite acceptable. Messages between 1-10 seconds give the user a sense of delay and require improvement \n"
        f"-\n Requests Slower than Average: {len(results_with_higher_than_average)}\n"
        f" \n Your response count of {len(response_times)} includes {len(results_with_higher_than_average)} that are above the average response time. If you observe an anomaly, repeat the test, if it is continuous, it requires improvement.\n"
        f"-\n Success Rate: {100 * len([r for r in results if r['status_code'] == 200]) / len(results):.0f}%\n"
        f" \n  of the requests sent during the test were responded to by the server.\n"
        f"-\n Throughput: {throughput:.2f} requests per second\n"
        f" \n This score can be used to compare the performance of the URL being tested against other scenarios."
    )

    response_data = {
        "results": results,
        "throughput": throughput,
        "summary_message": summary_message
    }

    return response_data

@app.route('/send_requests', methods=['GET', 'POST'])
def send_requests():
    form = RequestsForm()
    if request.method == 'POST':
        website_url = form.url.data
        num_users = form.num_users.data
        num_requests_per_user = form.num_requests_per_user.data

        if not website_url.startswith(('http://', 'https://')):
            website_url = 'https://' + website_url

        results = send_multiple_requests(website_url, num_users, num_requests_per_user)
        details_for_storage = {key: results[key] for key in results if key != 'summary_message'}
        serialized_details = json.dumps(details_for_storage)

        new_test_result = TestResult(
            test_type='send_requests',
            url=website_url,
            details=serialized_details,
            message=results['summary_message']
        )

        db.session.add(new_test_result)
        db.session.commit()

        return jsonify(results)

    return render_template('send_requests.html', form=form)


@app.route('/backend1/health')
def backend1_health():
    
    return '', 200

@app.route('/backend2/health')
def backend2_health():
    
    return '', 500

backend_servers = [
    'http://localhost:5000/backend1/health',
    'http://localhost:5000/backend2/health'
]

@app.route('/health_check')
def health_check():
    results = {}
    summary_messages = []
    
    for server in backend_servers:
        try:
            response = requests.get(server)
            if response.status_code == 200:
                results[server] = 'Healthy'
                summary_messages.append(f"{server} is HEALTHY.")
        except requests.exceptions.RequestException:
            results[server] = 'Unreachable'
            summary_messages.append(f"{server} is unreachable.")
    
    
    serialized_details = json.dumps(results)
    summary_message = " | ".join(summary_messages)
    
    
    new_test_result = TestResult(
        test_type='health-check',
        details=serialized_details,
        message=summary_message,
        url=','.join(backend_servers)  
    )
    db.session.add(new_test_result)
    db.session.commit()
    
    
    if request.headers.get('Accept') == 'application/json':
        return jsonify(results)  

    
    return render_template('health_check.html', results=results)



@app.route('/k6-load-test', methods=['GET', 'POST'])
def run_load_test():
    if request.method == 'POST':
        
        api_key = request.form['api_key']
        
        login_command = f'k6 login cloud --token {api_key}'
        login_process = subprocess.run(login_command, shell=True, capture_output=True, text=True)
        if login_process.returncode != 0:
            return render_template('load_test_output.html', output_message="Failed to authenticate with k6 Cloud.", error_message=login_process.stderr)

        url = request.form['url']
        stages_count = int(request.form.get('stages_count', 0))
        stages = []
        for i in range(1, stages_count + 1):
            stage_key_duration = f'duration{i}'
            stage_key_target = f'target{i}'
            if stage_key_duration in request.form and stage_key_target in request.form:
                try:
                    stages.append({
                        "duration": request.form[stage_key_duration],
                        "target": int(request.form[stage_key_target])
                    })
                except ValueError:
                    continue
        
        script_content = generate_k6_script(url, stages)
        script_filename = 'temp_k6_script.js'
        with open(script_filename, 'w') as file:
            file.write(script_content)

        csv_filename = 'load_test_results.csv'
        command = f'k6 cloud {script_filename}'
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if process.returncode == 0:
            match = re.search(r'(https?://[^\s]+)', process.stdout)
            analysis_url = match.group(0) if match else ""
            output_message = f'For detailed analysis, please <a href="{analysis_url}">click here</a>.' if match else "The analysis URL could not be found."
            error_message = ""
        else:
            output_message = process.stderr
            error_message = "Load test execution failed."

        return render_template('load_test_output.html', output_message=output_message, error_message=error_message, csv_file=csv_filename, analysis_url=analysis_url)
 
    return render_template('load_test_form.html')

def generate_k6_script(url, stages):
    options = {
        "stages": stages,
        "thresholds": {"http_req_duration": ["p(95)<500"]},
    }
    return f"""
import http from 'k6/http';
import {{ sleep }} from 'k6';

export let options = {json.dumps(options)};

export default function () {{
    http.get('{url}');
    sleep(1);
}}
"""


@app.route('/generate_report', methods=['GET', 'POST'])
def generate_report():
    if request.method == 'GET':
        return render_template('generate.html')
    elif request.method == 'POST':
        url = request.form['url']
        test_results = TestResult.query.filter_by(url=url).all()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        for result in test_results:
            elements.append(Paragraph(f"Test Type: {result.test_type}", styles['Heading2']))

            details = json.loads(result.details)

            if result.test_type == 'send_requests':
                
                data = [['User ID', 'Status Code', 'Response Time']] + [
                    [result['user_id'], result['status_code'], result['response_time']]
                    for result in details.get('results', [])
                ]
            else:
                
                data = [['Request Number', 'Status Code', 'Response Time']] + [
                    [detail['Request Number'], detail['Status Code'], detail['Response Time']]
                    for detail in details.get('details_of_requests_higher_than_average', [])
                ]

            detail_table = Table(data)
            detail_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ]))

            elements.append(detail_table)
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"Message: {result.message}", styles['BodyText']))
            elements.append(Spacer(1, 20))

        doc.build(elements)
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        buffer.close()
        
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
        return response



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)


 