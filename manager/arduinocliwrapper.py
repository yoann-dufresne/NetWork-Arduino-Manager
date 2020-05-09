import os
import sys


# --- Init module ---
# Define arduino cli location. If not localy present, assume that it's globally installed
curpath = os.path.dirname(os.path.abspath(__file__))
cli_location = '/'.join(str(curpath).split('/')[:-1]) + '/bin'
command = "arduino-cli"
if os.path.isdir(cli_location) and os.path.isfile(f"{cli_location}/arduino-cli"):
    command = f"{cli_location}/{command}"

# Test arduino-cli command
stream = os.popen(f"{command} version")
out = stream.read()
if not out.startswith("arduino-cli Version:"):
    print("Impossible to locate arduino-cli tool.\nPlease install it globally or inside of the bin directory here using the install.sh script.", file=sys.stderr)
    exit(1)


def _get_header_idxs(line, header_names):
    idxs = []
    for name in header_names:
        idx = line.find(name)
        if idx != -1:
            idxs.append((idx, name))

    return sorted(idxs)


def _out_to_dicts(text, header_names):
    lines = text.split('\n')

    header_idxs = _get_header_idxs(lines[0], header_names)

    values = []
    for line in lines[1:]:
        line_values = {name:'' for name in header_names}

        # Parse all the values
        for idx in range(len(header_idxs)-1):
            start = header_idxs[idx][0]
            stop = header_idxs[idx+1][0]
            val = line[start:stop].strip()
            line_values[header_idxs[idx][1]] = val
        # Parse last value
        start = header_idxs[-1][0]
        val = line[start:].strip()
        line_values[header_idxs[-1][1]] = val

        values.append(line_values)
    return values


# ----------------- Commands -----------------

def board_list():
    out = os.popen(f"{command} board list").read().strip()
    names = ["Port", "Type", "Board Name", "FQBN", "Core"]
    lines = _out_to_dicts(out, names)
    lines = filter(lambda x: True if x["Board Name"] != "Unknown" else False, lines)
    return lines

def core_list():
    out = os.popen(f"{command} core list").read().strip()
    names = ["ID", "Installed", "Latest", "Name"]
    return _out_to_dicts(out, names)

def core_install(board):
    print(f"Installing core library {board}")
    out = os.popen(f"{command} core install {board} --format text").read().strip()
    
    if out.startswith("Error"):
        print(out, file=sys.stderr)
        return False

    return True

def compile(fqbn, sketch_dir):
    sketch_name = sketch_dir[:-1].split('/')[-1]
    print(f"Compiling {sketch_name} for {fqbn} architecture")
    out = os.popen(f"{command} compile --fqbn {fqbn} {sketch_dir}").read().strip()
    lines = out.split("\n")
    
    if lines[-1].startswith("Error"):
        print(out, file=sys.stderr)
        return False

    return True

def upload(port, fqbn, sketch_dir):
    sketch_name = sketch_dir[:-1].split('/')[-1]
    print(f"Upoloading {sketch_name} on {port} for {fqbn} architecture")
    out = os.popen(f"{command} upload -p {port} --fqbn {fqbn} {sketch_dir}").read().strip()
    lines = out.split("\n")
    
    if lines[-1].startswith("Error"):
        print(out, file=sys.stderr)
        return False

    return True
