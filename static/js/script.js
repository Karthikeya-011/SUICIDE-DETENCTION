document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('prediction-form');
  const resultDiv = document.getElementById('result');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const text = document.getElementById('inputText').value.trim();

    if (!text) {
      alert('Please enter some text');
      return;
    }

    resultDiv.innerHTML = `<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>`;

    try {
      const response = await fetch('/suicide-ideation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text })
      });

      if (!response.ok) throw new Error('Network response was not ok.');

      const data = await response.json();

      let icon = '';
      let alertClass = 'alert-secondary';

      if (data.predictionText === 'Potential Suicide Post') {
        icon = '⚠️ ';
        alertClass = 'alert-danger';
      } else if (data.predictionText === 'Non Suicide Post') {
        icon = '✅ ';
        alertClass = 'alert-success';
      } else {
        icon = 'ℹ️ ';
      }

      resultDiv.innerHTML = `
        <div class="alert ${alertClass}" role="alert">
          Prediction: ${icon}<strong>${data.predictionText}</strong> (Confidence: ${data.prediction.toFixed(2)})
        </div>
      `;

      if (data.predictionText === 'Potential Suicide Post') {
        resultDiv.innerHTML += `
          <p>If you or someone you know is struggling, please consider reaching out to:</p>
          <ul>
            <li><a href="https://suicidepreventionlifeline.org/" target="_blank">Suicide Prevention Lifeline</a></li>
            <li><a href="https://www.mentalhealth.gov/get-help/immediate-help" target="_blank">MentalHealth.gov Immediate Help</a></li>
          </ul>
        `;
      }

    } catch (error) {
      resultDiv.innerHTML = `<div class="alert alert-warning">Error: ${error.message}</div>`;
    }
  });
});
