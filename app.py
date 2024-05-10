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

    # Check if the table exists
    if table:
        # Retrieving the rows of the table
        rows = table.find_all('tr')

        # Check if the second TR contains the club name
        club_row = rows[1] if len(rows) > 1 else None
        club_name = club_row.find('div', {'class': 'headers'}).text if club_row else None

        # Iterating through the rows to extract the data
        for row in rows[2:]:  # Skip the first two rows (headers and club name)
            # Extracting data from each column in the row
            cells = row.find_all(['td', 'th'])  # Including th tags in case they contain data
            data = [cell.text.strip() for cell in cells if cell.has_attr('class') and ('datas1' in cell['class'] or 'datas0' in cell['class'])]

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

    # Returning the number of results, club name, and records
    return jsonify({
        "club_name": club_name,
        "num_results": len(records),
        "records": records
    })

if __name__ == '__main__':
    app.run(debug=True)
