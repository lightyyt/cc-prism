#!/usr/bin/env python3
from base64 import b64encode
from sys import argv
from pathlib import Path
import json
import requests
lua_base = """local arc = {
    manifest = {
        name = "%NAME%",
        version = "%VERSION%",
        add_neon_entry = %ADD_NEON%,
        neon_label = "%NEON_LABEL%",
        neon_name = "%NEON_NAME%",
        neon_boot = "%NEON_BOOT%",
        root = "%ROOT%"
    },

    files = {
%FILES%
    }
}

"""

lua_append="""
local scp = term.setCursorPos
local fg = term.setTextColor
local bg = term.setBackgroundColor
bg(colors.blue)
fg(colors.white)
term.clear()
local w, h = term.getSize()
function cen(t, y)
    local m = math.floor
    scp(m(w/2)-m(#t/2), y)
    term.write(t)
end
cen("ARC Installer", 1)
fg(colors.lightGray)
for i=1,w,1 do
	scp(i,2)
	term.write("\\168")
end
fg(colors.white)
cen(arc.manifest.name,3)

cen("Would you like to install this to", 5)
local path="/arc/"..arc.manifest.root.."/"
cen(path, 6)

function cl(y)
	for i=1,w,1 do
		scp(i,y)
		term.write(" ")
	end
end

cen("[Y/N]> ",8)
while true do
	local _, k = os.pullEvent("key")
	if k == keys.y or k == keys.z then
		term.clear()
		cen("CC:Prism Installer", 1)
		fg(colors.lightGray)
		for i=1,w,1 do
			scp(i,2)
			term.write("\\168")
		end
		fg(colors.white)
		cen("Installing "..arc.manifest.name, 3)
		fs.makeDir(path)
		for i, v in pairs(arc.files) do
			cen("Extracting " .. i, 5)
			local dat = base64.decode(v)
			sleep(0.1)
			cl(5)
			cen("Creating " .. i, 5)
			local f = fs.open(path..i,"w")
			f.write(dat)
			f.close()
			sleep(0.1)
			cl(5)
		end
		sleep(0.1)
		--NEON

		if arc.manifest.add_neon_entry and fs.exists("/neon/boot") then
			cl(5)
			cen("Adding NEON Entry...", 5)
			local f = fs.open("/neon/boot/"..arc.manifest.neon_name..".eon", "w")
			f.write("EON=1\\nLABEL="..arc.manifest.neon_label.."\\nBOOT="..path..arc.manifest.neon_boot.."\\nINDEX="..#fs.list("/neon/boot")-1)
			f.close()
		end
		sleep(1)
		break
	elseif k == keys.n then
		break
	end
end

bg(colors.black)
fg(colors.white)
term.clear()
print("Goodbye!")
"""

print("Arc Builder for CC:Tweaked")

if len(argv) != 2:
    print("Please specify a directory!")
    exit(1)

dir_path = Path(argv[1])
if not dir_path.is_dir():
    print(f"{dir_path} is not a directory!")
    exit(1)


b64 = requests.get("https://raw.githubusercontent.com/iskolbin/lbase64/refs/heads/master/base64.lua")
lua_base+=b64.text.replace("return base64","")+lua_append


# Find first .arc.json file in the directory
json_file = None
for f in dir_path.glob("*.arc.json"):
    json_file = f
    break

if not json_file:
    print("No .arc.json file found in the directory!")
    exit(1)

with open(json_file, "r", encoding="utf-8") as f:
    meta = json.load(f)

src_path = dir_path / meta.get("src", "src")
if not src_path.is_dir():
    print(f"Source directory {src_path} does not exist!")
    exit(1)

# Encode files
arc_files = {}
for path in src_path.rglob("*"):
    if path.is_file():
        with open(path, "rb") as f:
            data = f.read()
            encoded = b64encode(data).decode("utf-8")
            rel_path = str(path.relative_to(src_path)).replace("\\", "/")
            arc_files[rel_path] = encoded

# Build Lua files table
files = ""
for fname, fdata in arc_files.items():
    files += f'        ["{fname}"] = "{fdata}",\n'
# Ensure root and neon_boot don't start or end with slashes
root = meta["root"].strip("/")

neon_boot = meta["neon_boot"].strip("/")

# Replace placeholders in lua_base
lua_code = lua_base.replace("%NAME%", meta["name"]) \
                   .replace("%VERSION%", meta["version"]) \
                   .replace("%ADD_NEON%", str(meta["add_neon_entry"]).lower()) \
                   .replace("%NEON_LABEL%", meta["neon_label"]) \
                   .replace("%NEON_BOOT%", neon_boot) \
                   .replace("%ROOT%", root) \
                   .replace("%NEON_NAME%", meta["neon_name"]) \
                   .replace("%FILES%", files)

output_file = Path(argv[1]) / "install.lua"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(lua_code)

print(f"Arc package created: {output_file}")
