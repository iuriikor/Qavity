@echo off
call C:/msys64/msys2_shell.cmd -clang64 -here -no-start -defterm -c "artiq_run %1; echo 'Command completed';