const ip = document.querySelector("div.content").getAttribute("data-ip")
const client = mqtt.connect(`mqtt://${ip}:9001`, {keepalive: 5, protocolVersion: 5})

client.subscribe({'led/status': {qos: 1}, 'button/status': {qos: 0}, 'photoresistor/status': {qos: 0}, 'state/join': {qos: 2}, 'state/leave': {qos: 2}}, (err, granted) => {
  if (err) {
    console.log(err)
  } else {
    console.log("Subscriptions granted", granted)
  }
})

client.on("connect", () => {
  console.log("Successfully connected to the MQTT broker")
})

client.on("reconnect", () => {
  console.log("Reconnection started to the MQTT broker")
})

client.on("disconnect", () => {
  console.log("Connection closed to the MQTT broker")
})

client.on("offline", () => {
  console.log("Connection offline to the MQTT broker")
})

client.on("error", (error) => {
  console.log("Error on parsing or connection to the MQTT broker:", error)
})

client.on("message", (topic, message) => {
  // message is Buffer
  let payloadStr = message.toString()
  console.log("Received message:", topic, payloadStr);
  let article = null
  const regex = /\((\d+)\)/
  switch (topic) {
    case "led/status":
      splitList = payloadStr.split(";")
      article = document.querySelector(`.content article[data-id="${splitList[0]}"]`)
      if (article.getAttribute("data-session-id") != splitList[1])
        break;
      let ledContainer = article.querySelector(".led-container")
      switchLed(ledContainer, Boolean(Number(splitList[2])))
      break;
    case "button/status":
      splitList = payloadStr.split(";")
      article = document.querySelector(`.content article[data-id="${splitList[0]}"]`)
      if (article.getAttribute("data-session-id") != splitList[1])
        break;
      let btnContainer = article.querySelector(".push-button-container")
      switchButton(btnContainer, Boolean(Number(splitList[2])))
      break;
    case "photoresistor/status":
      splitList = payloadStr.split(";")
      article = document.querySelector(`.content article[data-id="${splitList[0]}"]`)
      if (article.getAttribute("data-session-id") != splitList[1])
        break;
      while (chartMap[splitList[0]].data.labels.length >= 10) {
        chartMap[splitList[0]].data.labels.shift()
        chartMap[splitList[0]].data.datasets.forEach((dataset) => {
          dataset.data.shift()
        })
      }
      chartMap[splitList[0]].data.labels.push(new Date().timeNow())
      chartMap[splitList[0]].data.datasets.forEach((dataset) => {
        dataset.data.push(Number(splitList[2]))
      })
      chartMap[splitList[0]].update()
      break;
    case "state/join":
      if (!payloadStr.includes(";"))
        break;
      splitList = payloadStr.split(";")
      article = document.querySelector(`.content article[data-id="${splitList[0]}"]`)
      if (article == null) {
        fetch(`/sensor/${splitList[0]}`)
          .then(response => response.text()) // TODO: Manage errors here if server malfunctions
          .then(data => {
            document.querySelector(".content article").insertAdjacentHTML("beforebegin", data)
            let contentHeader = document.querySelector(".content header h2")
            let newStr = "(" + (Number(contentHeader.innerText.match(regex)[1]) + 1) + ")"
            contentHeader.innerText = contentHeader.innerText.replace(regex, newStr)
          })
          .catch(error => console.error(error));
      } else {
        article.getAttribute("data-session-id", splitList[1])
      }
      break;
    case "state/leave":
      splitList = payloadStr.split(";")
      article = document.querySelector(`.content article[data-id="${splitList[0]}"]`)
      if (article.getAttribute("data-session-id") != splitList[1])
        break;
      article.remove()
      let contentHeader = document.querySelector(".content header h2")
      let newStr = "(" + (Number(contentHeader.innerText.match(regex)[1]) - 1) + ")"
      contentHeader.innerText = contentHeader.innerText.replace(regex, newStr)
      break;
  }
});

// Dynamically switch LED image between bright/dark according to checkbox
const ledInputs = document.querySelectorAll(".led-container input[type='checkbox']")
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
  let article = this.closest("article")
  let sensorID = article.getAttribute("data-id")
  let sensorSessionID = article.getAttribute("data-session-id")
  let ledImg = article.querySelector(".led-container img.led-image")
  switchLedImage(ledImg, this.checked)
  fetch(`/led/${sensorID}?cmd=${Number(this.checked)}&ssnid=${sensorSessionID}`).then(response => {
    console.log(`Led on sensor [${sensorID}] requested to state [${this.checked}]. Response:`, response)
  })
  // TODO: Could also use MQTT to control sensor LED instead of GET request
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

// For the time now
Date.prototype.timeNow = function () {
     return ((this.getHours() < 10)?"0":"") + this.getHours() +":"+ ((this.getMinutes() < 10)?"0":"") + this.getMinutes() +":"+ ((this.getSeconds() < 10)?"0":"") + this.getSeconds();
}

const contexts = document.querySelectorAll("article .light-chart canvas")
let chartMap = {}
contexts.forEach((ctx) => {
  const id = ctx.closest("article").getAttribute("data-id")
  let chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: 'Luminosité',
        data: [],
        borderWidth: 3,
        borderColor: 'rgb(255, 99, 132)',
        fill: false,
        cubicInterpolationMode: 'monotone',
        tension: 0.4
      }]
    },
    options: {
      color: '#333',
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Chart.js Line Chart - Cubic interpolation mode'
        },
        legend: {
          display: false
        },
        title: {
          display: false
        }
      },
      interaction: {
        intersect: false,
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: 'Estampille temporelle en UTC'
          }
        },
        y: {
          display: true,
          title: {
            display: true,
            text: 'Valeur en %'
          },
          min: 0,
          max: 100,
          ticks: {
            callback: function(value, index, ticks) {
              return value + "%";
            }
          }
        }
      }
    }
  })
  chartMap[id] = chart
})

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
