import requests
for i in range(21):
    try:
        # URL of the file you want to download
        url = f'https://www.udt.gov.pl/images/kwalifikacje_osob_przykladowe_pytania/{i}.pdf'
        # Send a GET request to the URL with stream=True
        print(f"Getting: {url}")
        with requests.get(url, stream=True) as response:
            response.raise_for_status()  # Raise an error for bad responses
            with open(f'{i}.pdf', 'wb') as file:
                # Iterate over the response in chunks
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        print(f"Large PDF file downloaded and saved as '{i}.pdf'")
    except:
        pass