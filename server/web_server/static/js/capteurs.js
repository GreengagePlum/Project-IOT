// Dynamically switch LED image between bright/dark according to checkbox
let ledInputs = document.querySelectorAll(".led-container input[type='checkbox']")
function switchLedImage(ledImg, isLit) {
  if (ledImg.classList.contains("active") && !isLit) {
    ledImg.classList.remove("active")
  } else if (!ledImg.classList.contains("active") && isLit) {
    ledImg.classList.add("active")
  }
}
function switchLed(ledContainer, isLit) {
  let img = ledContainer.querySelector("img.led-image")
  let checkbox = ledContainer.querySelector("#led-toggle")
  switchLedImage(img, isLit)
  checkbox.checked = isLit
}
ledInputs.forEach((el) => el.addEventListener("change", function(event) {
  // event.preventDefault()
  let ledImg = this.closest(".led-container").querySelector("img.led-image")
  switchLedImage(ledImg, this.checked)
}))

// Switch a sensor's button display to pressed or unpressed
function switchButton(buttonContainer, isPushed) {
  let btnImg = buttonContainer.querySelector("img.push-button-image")
  let btnLabel = buttonContainer.querySelector("p.push-button-status")
  if (isPushed) {
    btnImg.src = "/static/assets/buttons/pressed-button-arrow-v2.png"
    btnLabel.innerText = "(appuyé)"
  } else {
    btnImg.src = "/static/assets/buttons/unpressed-button.png"
    btnLabel.innerText = "(relaché)"
  }
}

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
