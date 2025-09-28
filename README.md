# cc-prism
A simple ComputerCraft Installer Creation tool
https://github.com/iskolbin/lbase64/blob/master/base64.lua is used for base64 decoding in the ARC program

## Usage
Create a "[project_name].arc.json" file for your program, with this format: 
```json
{
  "name": "Program Name",
  "version": "1.0",
  "add_neon_entry": true,
  "neon_label": "Label Used by CC-NEON",
  "neon_name": "testprogram",
  "neon_boot": "start_file",
  "root": "/program",
  "source": "src"
}
```
if you disable add_neon_entry (set it to false) then you can leave everything neon related blank.

"name" is the name of your application

"version" is the version

"add_neon_entry" specifies that (if neon is installed) the program will have it's own boot entry in NEON

"neon_label" will specify the text in the NEON boot menu

"neon_name" is the filename of the .eon file

"neon_boot" is the .lua file that gets executed. (the lua file is by default in your program dir, so here it's /program/start_file.lua)

"root" is the location your program will be installed in (inside the arc folder)

"source" is the directory of your source code.

Your program will always be inside the /arc folder.
E.g. /arc/program/start_file.lua

Then, once you're done, simply run:

`./main.py [project_directory]` ([project_directory] is the folder where the .arc.json file is in, not your "source" folder!)
