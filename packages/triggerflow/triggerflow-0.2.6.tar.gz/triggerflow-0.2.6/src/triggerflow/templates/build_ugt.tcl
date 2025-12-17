file mkdir prj_{{ MODEL_NAME }}

open_project -reset prj_{{ MODEL_NAME }}

set_top {{ MODEL_NAME }}_GT

set core_files "model-gt.cpp {{ MODEL_NAME }}_project.cpp"

if { [file exists "BDT.cpp"] } {
    set all_files "$core_files BDT.cpp"
} else {
    set all_files "$core_files"
}

add_files $all_files -cflags "-std=c++11 -I../"

open_solution -reset solution1
set_part {xc7vx690t-ffg1927-2}

create_clock -period 25
set_clock_uncertainty 0


config_array_partition -complete_threshold 2

csynth_design

file mkdir firmware
file mkdir firmware/hdl
file mkdir firmware/hdl/payload
file mkdir firmware/hdl/payload/gtl
file mkdir firmware/hdl/payload/gtl/model
file mkdir firmware/cfg

set f [open firmware/cfg/model.dep "w"]

if {[file exists prj_{{ MODEL_NAME }}/solution1/syn/vhdl]} {
    foreach filepath [glob -nocomplain prj_{{ MODEL_NAME }}/solution1/syn/vhdl/*] {
        set filename [file tail $filepath]
        file copy -force $filepath firmware/hdl/payload/gtl/model/$filename
        puts $f "src payload/gtl/model/$filename"
    }
}

close $f
exit
