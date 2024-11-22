import fitz  # PyMuPDF
import json
import sys
import os
import io
from PIL import Image
data = []

def main() -> None:
    #if no argv present displays help
    if(len(sys.argv) == 1):
        help()
    else:
        #if -h flag displays help
        if(sys.argv[1] == '-h'):
            help()
        
        #single file mode
        elif (len(sys.argv) == 4 and sys.argv[1] != '-d'):

            data = []
            output_folder = 'images/'
            file_path = sys.argv[1]
            texttxt = read_pdf(file_path)

            #getting images from pdf
            extract_images_from_pdf(file_path, output_folder)

            #reading flags about removing Polish characters
            if(sys.argv[3] == '-y'):
                data = text_to_json(texttxt, sys.argv[2], True)
            elif(sys.argv[3] == '-n'):
                data = text_to_json(texttxt, sys.argv[2], False)

            #wiriting data to json and html
            pathToJson = write_to_json(data, 'data.json')
            generate_HTML(read_json(pathToJson), 'generate.html')

        #directory mode
        elif (len(sys.argv) == 5 and sys.argv[1] == '-d'):
            answerFiles = []
            counter = 0

            #getting answers files
            for asf in get_files_from_folder(sys.argv[3]):
                answerFiles.append(asf)
            
            #getting and reading pdfs
            for file in get_files_from_folder(sys.argv[2]):
                #creates paths for every file
                data = []
                name = file[:-4]
                root_folder_for_file = f'out{name}/'
                output_folder_images = f"{root_folder_for_file}images_{name}/"
                output_html_name = f"{root_folder_for_file}/{name}.html"

                #reads pdf
                text = read_pdf(f'{sys.argv[2]}/{name}.pdf')

                #reading flags for deleting Polish characters
                if(sys.argv[4] == '-y'):
                    data = text_to_json(text, answerFiles[counter], True,)
                elif(sys.argv[4] == '-n'):
                    data = text_to_json(text, answerFiles[counter], False,)

                #getting images to separate folder
                extract_images_from_pdf(f'{sys.argv[2]}/{name}.pdf', output_folder_images)

                #writing data and generating html
                pathToJson = write_to_json(data, f'{root_folder_for_file}/data.json')
                generate_HTML(read_json(pathToJson),output_html_name)

                #updating counter for getting correct answer file
                counter += 1

#constains help for runnig program
def help() -> None:
    h = """
         _________
        |Auto Quiz|
Po nazwie pliku umiesc argumenty np:
    -h for help
    -y for delete polish chars from output
    -n for save polish chars if output
    -d for multiple files at once
    Dla pojedynczego pliku:
        Linux:
        python3 pdfread.py sciezka_do_pdfa.pdf sciezka_do_odpowiedzi.txt -y/n
    
        Windows:
        python3 pdfread.py sciezka_do_pdfa.pdf sciezka_do_odpowiedzi.txt -y/n
    
    Dla folderu z plikami pdf i folderu z odpowiedziami:
        Linux:
        python3 pdfread.py -d folder_z_pdfami folder_z_odpowiedziami -y/n
    
        Windows:
        python3 pdfread.py -d folder_z_pdfami folder_z_odpowiedziami -y/n
"""
    print(h)

#gets all files in direcotry only pdf or txt(for answers) type
def get_files_from_folder(folder) -> list:

    # List all files in the directory
    files = os.listdir(folder)

    # Filter out only files (not directories)
    files = [f for f in files if os.path.isfile(os.path.join(folder, f))]
    tmp = []
    for f in files:
        if(f[-1] == "f"and f[-2] == "d" and f[-3] == 'p' and f[-4] == '.'):
            tmp.append(f)
        elif(f[-1] == 't' and f[-2] == 'x' and f[-3] == 't'):
            tmp.append(f)

    return(tmp)

#gets every image from pdf file
def extract_images_from_pdf(pdf_path, output_folder) -> None:
    counter = 0
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    
    # Loop through each page
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        images = page.get_images(full=True)
        
        # Extract each image
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image = Image.open(io.BytesIO(image_bytes))
            
            # Save image as pageX_Y.ext (X = page number, Y = image index)
            image_filename = f"page{page_number + 1}_{img_index + 1}.{image_ext}"
            image_path = os.path.join(output_folder, image_filename)
            image.save(image_path)
            counter += 1
            print(f"Saved image at: {image_path}")

    print(f'Saved {counter} images at <{output_folder}>')
    

#making json from array of text by line
def text_to_json(text, ansFilePath, deletePolishChars) -> list:
    # declaring variables
    data = []
    tmptextbylines = []
    answers = []
    i = 0
    questionNum = 0
    tmpline = ""
    questionS = ""
    correctAnswer = ""
    answerAS = ""
    answerBS = ""
    answerCS = ""
    answerDS = ""

    if deletePolishChars:
        # making array of lines in text and removing Polish characters
        textbylines = str(text).split("\n")
        for line in textbylines:
            tmpline = ""
            for word in line.split(' '):
                wordc = convert_polish_chars(word)
                tmpline += wordc 
                tmpline += ' '
            tmptextbylines.append(tmpline)
        textbylines = tmptextbylines
    else:
        # when not removing Polish characters, just split text into lines
        textbylines = str(text).split("\n")
    
    print(f'Reading and analyzing answers file <{ansFilePath}>')

    # Reading and extracting answers from answers file
    try:
        with open(ansFilePath, 'r') as ansf:
            answers = ansf.readlines()
        for j in range(len(answers)):
            answers[j] = answers[j].rstrip('\n')[-1].upper()
    except FileNotFoundError:
        print(f"Error: The answers file <{ansFilePath}> was not found.")
        return []
    except Exception as e:
        print(f"Error reading the answers file: {e}")
        return []

    while i < len(textbylines) - 1:
        # printing progress
        if i % 150 == 0:
            print(f"Converting Data >> {round((i / (len(textbylines) - 1)) * 100, 1)}%")
        
        # check for question number and get question text
        if is_integer(textbylines[i]):
            questionNum = int(textbylines[i])
            if questionNum - 1 < len(answers):
                correctAnswer = answers[questionNum - 1]
            else:
                print(f"Warning: No answer found for question {questionNum}")
                correctAnswer = ""
            numNext = 0
            i += 1
            while i + numNext < len(textbylines) and textbylines[i + numNext][0] != ' ':
                questionS += textbylines[i + numNext].rstrip('\n')
                numNext += 1
        
        # check for answer A
        elif textbylines[i][:3] == 'a )':
            numNext = 1
            answerAS += textbylines[i][4:].rstrip('\n')
            while i + numNext < len(textbylines) and textbylines[i + numNext][:3] != 'b )':
                answerAS += textbylines[i + numNext].rstrip('\n')
                numNext += 1
        
        # check for answer B
        elif textbylines[i][:3] == 'b )':
            numNext = 1
            answerBS += textbylines[i][4:].rstrip('\n')
            while i + numNext < len(textbylines) and textbylines[i + numNext][:3] != 'c )':
                answerBS += textbylines[i + numNext].rstrip('\n')
                numNext += 1
        
        # check for answer C
        elif textbylines[i][:3] == 'c )':
            numNext = 1
            answerCS += textbylines[i][4:].rstrip('\n')
            while i + numNext < len(textbylines) and textbylines[i + numNext][:3] != 'd )':
                answerCS += textbylines[i + numNext].rstrip('\n')
                numNext += 1
        
        # check for answer D and reset variables
        elif textbylines[i][:3] == 'd )':
            numNext = 1
            answerDS += textbylines[i][4:].rstrip('\n')
            while i + numNext < len(textbylines) and textbylines[i + numNext][0] != ' ':
                answerDS += textbylines[i + numNext].rstrip('\n')
                numNext += 1

            # temporary JSON data instance
            tmp = {
                "questionNumber": questionNum,
                "questionText": questionS,
                "correctAnswer": correctAnswer,
                "answerA": answerAS,
                "answerB": answerBS,
                "answerC": answerCS,
                "answerD": answerDS
            }

            # appending data to JSON buffer
            data.append(tmp)

            # resetting
            questionNum = 0
            questionS = ""
            correctAnswer = ""
            answerAS = ""
            answerBS = ""
            answerCS = ""
            answerDS = ""
        
        i += 1

    return data

#writes data to json file
def write_to_json(data, output_file) -> str:
    path = output_file
    print(f"Writing data to JSON <{path}>")
    with open(path,'w',encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return path

#deletes any polish non utf-8 chars
def convert_polish_chars(word) -> str:
    # Dictionary mapping Polish special characters to their ASCII equivalents
    polish_to_ascii = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l',
        'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L',
        'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
    }
    
    # Convert each character in the word using the dictionary
    converted_word = ''.join(polish_to_ascii.get(char, char) for char in word)
    
    return converted_word


#read data from json file
def read_json(path) -> list:
    print(f"Reading data from JSON <{path}>")
    datafromjson = []
    with open(path,'r',encoding='utf-8') as f:
        datafromjson = json.load(f)
    return datafromjson

#check if chat id integer
def is_integer(s) -> bool:
    try:
        int(s)
        return True
    except:
        return False

#read text from pdf file
def read_pdf(file_path) -> str:
    print(f"Reading pdf <{file_path}>")
    texttxt = "" 
    pdf_document = fitz.open(file_path)

    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        
        texttxt += page.get_text("text")  # Default extraction

    return texttxt

#generate text and writes it to html file
def generate_HTML(data, pathToHtml) -> str:
    print("Making HTML...")
    html = ""
    head = """
<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Test 1</title>
  <link rel="stylesheet" href="style.css">
  <script src="script.js"></script>
</head>
<body>

  <div id="score-container">
    <p>Odpowiedzi:</p>
    <p><span id="correct-count" class="green circle">0</span> <span id="incorrect-count" class="red circle">0</span></p>
  </div>
  

  <h2>Nazwa testu</h2>

  <div class="test-content">"""
    html += head
    for item in data:
        html += f"""
    <div class="question-box">
      <div class="question">
        <p><strong>{item['questionNumber']}.</strong> {item["questionText"]}
        </p>
        <div class="answers">
          <button onclick="checkAnswer(this, 'A', '{item["correctAnswer"]}')">A: {item['answerA']}
          </button>
          <button onclick="checkAnswer(this, 'B', '{item["correctAnswer"]}')">B: {item['answerB']}
          </button>
          <button onclick="checkAnswer(this, 'C', '{item["correctAnswer"]}')">C: {item['answerC']}
          </button>
          <button onclick="checkAnswer(this, 'D', '{item["correctAnswer"]}')">D: {item['answerD']}
          </button>
        </div>
        <p class="feedback" style="display: none;"></p>
      </div>
    </div>"""
    tail = """</div>
</body>
</html> """
    html += tail

    #creates html file
    with open(pathToHtml,'w') as f:
        f.write(html)
    print(f'HTML file generated as <{pathToHtml}>')


if __name__ == "__main__":
    main()