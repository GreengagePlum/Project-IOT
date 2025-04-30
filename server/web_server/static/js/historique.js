
// Local filtering function to filter sensor names
document.addEventListener('DOMContentLoaded', function () {
  const searchInput = document.querySelector('.search-bar');

  searchInput.addEventListener('input', function () {
    const filter = searchInput.value.toLowerCase();
    const articles = document.querySelectorAll('article');

    articles.forEach(article => {
      const h3 = article.querySelector('h3');
      const text = h3 ? h3.textContent.toLowerCase() : '';

      if (text.includes(filter)) {
        article.style.display = '';
      } else {
        article.style.display = 'none';
      }
    });
  });
});
