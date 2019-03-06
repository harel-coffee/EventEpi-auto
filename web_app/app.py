from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
import sys
sys.path.insert(0, '/home/auss/github/nlp-surveillance')
from nlp_surveillance.scraper.text_extractor import extract_cleaned_text_from_url
from nlp_surveillance.classifier.summarize import annotate_and_summarize
from nlp_surveillance.pipeline import TrainNaiveBayes

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)


@app.route('/images/<path:path>')
def send_png(path):
    return send_from_directory('images', path)


@app.route('/square', methods=['POST'])
def square():
    url = str(request.form.get('url_input', 0))
    text = extract_cleaned_text_from_url(url)
    parsed = annotate_and_summarize(text,
                                    TrainNaiveBayes('dates').data_output(),
                                    TrainNaiveBayes('counts').data_output(),
                                    )
    parsed_as_dict = {'country': parsed["geoname"][0],
                      'confirmed': int(sum(parsed["counts"][0])/len(parsed["counts"][0])),
                      'disease': parsed["diseases"][0],
                      'date': parsed["date"][0][0][0].strftime("%d, %B, %Y")}
    parsed_formatted = (f'In {parsed_as_dict["country"]} are around {parsed_as_dict["confirmed"]} confirmed cases of '
                        f'{parsed_as_dict["disease"]} as of {parsed_as_dict["date"]}')
    data = {'parsed_formatted': str(parsed_formatted), 'as_dict': parsed_as_dict}

    if not os.path.isfile('js/table.json'):
        with open('js/table.json', 'w') as f:
            data_dict = {'data': [data['as_dict']]}
            json.dump(data_dict, f)
    else:
        with open('js/table.json') as f:
            data_dict = json.load(f)
            data_dict['data'].append(data['as_dict'])
            json.dump(data_dict, f)
    data = jsonify(data)
    return data


if __name__ == '__main__':
    app.run(debug=True)