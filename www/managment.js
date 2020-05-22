
let list_sketches = function(callback) {
  fetch('/sketches')
  .then(response => response.text())
  .then(data => callback(data));
};
let available_sketches = [];
list_sketches((text)=> {
  available_sketches = text.split(',');
});

let list_arduinos = function(callback) {
  fetch('/arduinos')
  .then(response => response.text())
  .then(data => callback(data));
};


let create_select_sketch = function(old_prog) {
  sketches = [];
  for (let s of available_sketches)
    sketches.push(s);
  if (!sketches.includes(old_prog))
    sketches.push(old_prog);

  sketches.sort();

  let sel = "<select>";
  for (let s of sketches) {
    sel += "<option value='" + s + "'";;
    if (s == old_prog){
      sel += "class='sketch_ready' selected"
    }
    sel += ">" + s + "</option>";
  }
  sel += "</select>";
  return sel;
}


let ard_table = document.getElementById("arduinos");
let update_arduino_list = function(port, board, serial, sketch) {
  if (port == "None") port = "";
  if (sketch == "None") sketch = "";

  let line = document.getElementById(serial);
  // Create a new entry if the board was unknown
  if (line == null) {
    ard_table.innerHTML += "<tr class='arduino " + (port == "" ? "disconnected" : "connected") + "' id='" + serial + "'>" + "<td class='port'>" + port + "</td>" + "<td class='board'>" + board + "</td>" + "<td class='serial'>" + serial + "</td>" + "<td class='sketch' hidden_value='" + sketch + "'><span class='name'>" + sketch + "</span><span class='select'>" + create_select_sketch(sketch) + "</span></td><td class='upload'><img src='/upload.png'/></td>" + "</tr>";
    line = document.getElementById(serial);
    let sel = line.querySelector("select");
    sel.onchange = function(data) {
      let img = line.querySelector("img");
      img.onclick = () => {
        console.log("/upload/" + serial + "/" + sel.value);
        fetch("/upload/" + serial + "/" + sel.value);
      };
    }
  }
  // Update the board status regarding the port
  let prev_port = line.querySelector('.port');
  let port_changed = false;
  if (port != prev_port.innerHTML) {
    prev_port.innerHTML = port
    port_changed = true;

    if (port == "") {
      line.classList.remove("connected");
      line.classList.add("disconnected");
    } else {
      line.classList.remove("disconnected");
      line.classList.add("connected");
    }
  }
  // Update the uploaded sketch status
  let td_sketch = line.querySelector('.sketch');
  let prev_sketch = td_sketch.querySelector('.name').innerHTML;

  if (sketch != prev_sketch) {
    td_sketch.innerHTML = "<span class='name'>" + sketch + "</span><span class='select'>" + create_select_sketch(sketch) + "</span>";
    let sel = td_sketch.querySelector("select");
    sel.onchange = function(data) {
      let img = line.querySelector("img");
      img.onclick = () => {
        console.log("/upload/" + serial + "/" + sel.value);
        fetch("/upload/" + serial + "/" + sel.value);
      };
    }
  }
}

let interval = setInterval(()=>{list_arduinos(function(text) {
  for (let line of text.split("\n")) {
    let sp = line.split("\t");
    update_arduino_list(sp[0], sp[1], sp[2], sp[3]);
  }
});}, 3000);
