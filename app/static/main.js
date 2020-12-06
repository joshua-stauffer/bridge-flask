import { api } from './apiEndpoints.js';
const headers = {
  method: 'GET',
  mode: 'same-origin',
  cache: 'default',
  credentials: 'same-origin',
  headers: {
    'Content-Type': 'application/json'
  }
}
fetch(api.quote_api, headers)
  .then(response => response.json())
  .then(data => {
    function changeQuote() {
      const quote = data[Math.floor(Math.random() * data.length)];
      const quoteblock = document.querySelector('.quotation');
      const citation = document.querySelector('.quote-author');
      quoteblock.textContent = quote.text;
      citation.textContent = quote.author;
      setTimeout(changeQuote, 10000)
    }
    changeQuote()
  })