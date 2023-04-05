@echo off
echo Generating skill resources
call gen_skill_resources.bat
cd scripts
echo Generating character resources
call gen_chara_resources.bat
cd scripts
echo Generating support card resources
call gen_support_card_resources.bat
cd scripts
pause