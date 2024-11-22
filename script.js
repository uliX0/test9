let correctAnswers = 0;
let incorrectAnswers = 0;


function loadTest(testFile) {
    correctAnswers = 0;
    incorrectAnswers = 0;
     
    const container = document.getElementById('test-container');

    container.innerHTML = '<p>Ładowanie testu...</p>';

    fetch(testFile)
      .then(response => {
        if (!response.ok) {
          throw new Error('Błąd ładowania testu');
        }
        return response.text();
      })
      .then(data => {
        container.innerHTML = data;
      })
      .catch(error => {
        container.innerHTML = `<p style="color: red;">Nie udało się załadować testu: ${error.message}</p>`;
      });
  }

  function checkAnswer(button, chosen, correct) {
    const questionDiv = button.parentElement.parentElement;
    const feedback = questionDiv.querySelector('.feedback');
    const buttons = questionDiv.querySelectorAll('button');
    
    if (feedback.style.display === 'block') {
      return;
    }
  
    buttons.forEach(btn => btn.disabled = true);
  
    
    if (chosen === correct) {
      correctAnswers++;
      feedback.textContent = "Gratulacje! To poprawna odpowiedź.";
      feedback.className = "feedback correct";
      button.classList.add("correct"); 
    } else {
      incorrectAnswers++;
      feedback.textContent = `Niestety, to nie jest poprawna odpowiedź. Poprawna odpowiedź to: ${correct}.`;
      feedback.className = "feedback incorrect";
      button.classList.add("incorrect"); 
  
      
      buttons.forEach(btn => {
        if (btn.textContent.trim().startsWith(correct + ":")) {
          btn.classList.add("correct");
        }
      });
    }
  
    
    feedback.style.display = 'block';
    document.getElementById('correct-count').textContent = correctAnswers;
    document.getElementById('incorrect-count').textContent = incorrectAnswers;
  }
  
  