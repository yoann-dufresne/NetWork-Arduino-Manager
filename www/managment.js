
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

let ard_div = document.getElementById("arduinos");
let interval = setInterval(()=>{list_arduinos(function(text) {
  content = "<table><tr><td>Port</td><td>Board type</td><td>Serial number</td><td>Linked sketch</td></tr>";
  for (let line of text.split("\n")) {
    let sp = line.split("\t");
    content += "<tr class='arduino'>" + "<td class='port'>" + sp[0] + "</td>" + "<td class='board'>" + sp[1] + "</td>" + "<td class='serial'>" + sp[2] + "</td>" + "<td class='sketch'>" + sp[3] + "</td>" + "</tr>";
  }
  content += "</table>";
  ard_div.innerHTML = content;
});}, 3000);
