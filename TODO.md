# TODO

## Bugs & Fixes

- [ ] Use a time scale instead of a simple Cartesian scale in Chartjs
  - [ ] Polish initial display of data
  - [ ] Implement a scrolling update animation
- [ ] Make the browser MQTT client more robust
  - [ ] Create a task on a timer via `setInterval()` to cleanup disconnected ESP32s
    - [ ] Keep track of last seen timestamps for each ESP32
  - [ ] Include logic to always try and fetch an ESP32 if any kind of message comes for a seemingly inexistant ESP32 (thus without a proper `state/join` that was captured, "page load data race")
- [ ] Cleanup JS

## Features

- [ ] Implement sensor name editing
- [ ] Show if MQTT offline in browser
- [ ] Ensure responsiveness
- [ ] Add home page (with real life pictures of the setup)
- [ ] Implement layout toggle
- [ ] Password protect MQTT
  - [ ] Add authenticity checks via crypto (?)

## Configuration

- [ ] Dockerize
- [ ] CI/CD

## Miscellaneous

- [ ] Test on other machines/browsers
- [ ] Add better hierarchy to MQTT channels
- [ ] Add EN/FR language switch to the website
  - [ ] Translate website

## Done

- [x] Test on RBPi 3
  - [-] Check if in memory sqlite makes a performance difference
- [x] Add charts
- [x] Cleanup HTML and CSS
- [x] Chop up CSS into logical units
- [x] Write backend server
  - [-] Implement websockets or sse
- [x] Show error message when no js available
- [x] Implement UI updates
  - [x] LED state changes
  - [x] Button state changes
- [x] Implement filter bar logic
- [x] Chop up HTML into logical units
- [x] Create git repo
