const headers = {
  method: 'GET',
  mode: 'same-origin',
  cache: 'default',
  credentials: 'same-origin',
  headers: {
    'Content-Type': 'application/json'
  }
}
fetch("/api/qt-data", headers)
  .then(response => response.json())
  .then(data => {
    if (!data) return;
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

const toggleMenu = document.getElementById('toggle-menu')
const menu = document.getElementById('menu')

toggleMenu.addEventListener('click', () => {
  menu.classList.length > 1 ? 
    menu.className = 'navbar-list'
    : menu.className = 'navbar-list folded'
})

