
let list_sketches = function(callback) {
  fetch('/sketches')
  .then(response => response.text())
  .then(data => callback(data));
};

let list_arduinos = function(callback) {
  fetch('/arduinos')
  .then(response => response.text())
  .then(data => callback(data));
};


let ard_table = document.getElementById("arduinos");
let update_arduino_list = function(port, board, serial, sketch) {
  if (port == "None")
    port = "";

  let line = document.getElementById(serial);
  if (line == null) {
    ard_table.innerHTML += "<tr class='arduino' id='" + serial + "'>" + "<td class='port'>" + port + "</td>" + "<td class='board'>" + board + "</td>" + "<td class='serial'>" + serial + "</td>" + "<td class='sketch'>" + sketch + "</td>" + "</tr>";
    line = document.getElementById(serial);
  }
  let prev_port = line.querySelector('.port');
  if (port != prev_port.innerHTML)
    prev_port.innerHTML = port
  let prev_sketch = line.querySelector('.sketch');
  if (sketch != prev_sketch.innerHTML)
    prev_sketch.innerHTML = sketch
}

let interval = setInterval(()=>{list_arduinos(function(text) {
  for (let line of text.split("\n")) {
    let sp = line.split("\t");
    update_arduino_list(sp[0], sp[1], sp[2], sp[3]);
  }
});}, 3000);
