from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/records/<frmannee>/<frmclub>/<frmepreuve>')
def get_records(frmannee, frmclub, frmepreuve):
    # Mapping simplified inputs to corresponding epreuve codes
    epreuve_mapping = {
        "10": "261",  # 10km
        "5": "252",   # 5km
        "21": "271",  # Half marathon
        "42": "295"   # Marathon
    }

    # Checking if the frmepreuve exists in the mapping, otherwise default to the input value
    frmepreuve_code = epreuve_mapping.get(frmepreuve, frmepreuve)

    # Constructing the URL with parameters
    url = f"https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=bilans&frmmode=2&frmespace=0&frmannee={frmannee}&frmepreuve={frmepreuve_code}&frmnom=&frmprenom=&frmlicence=&frmclub={frmclub}&frmligue=&frmdepartement="

    # Retrieving the HTML content of the page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Finding the table containing the records
    table = soup.find('table', {'id': 'ctnBilans'})

    # List to store the data
    records = []

    # Checking if the table exists
    if table:
        # Retrieving the rows of the table
        rows = table.find_all('tr')

        # Iterating through the rows to extract the data
        for row in rows:
            # Extracting data from each column in the row
            cells = row.find_all(['td', 'th'])  # Including th tags in case they contain data
            data = [cell.text.strip() for cell in cells if cell.has_attr('class') and ('datas1' in cell['class'] or 'datas2' in cell['class'])]

            # Checking if the first field is empty
            if data and data[0] != "":
                # Adding the data to the records list
                records.append({
                    "name": data[0],
                    "category": data[1],
                    "event": data[2],
                    "time": data[3],
                    "gender": data[4],
                    "date": data[5],
                    "city": data[6]
                })

        # Returning the records or "No data" message with appropriate HTTP status code
        return (jsonify(records), 200) if records else (jsonify({"message": "No data"}), 404)
    else:
        # Returning an error message with HTTP status code 500
        return jsonify({"error": "Table not found"}), 500

if __name__ == '__main__':
    app.run(debug=True)
