cd dev_env
cd Scripts
call activate.bat
cd ..
cd ..
cd examples
REM cd mapdl_tyre_performance
cd generic_api

set TOKEN=

REM python project_setup.py --name "Jons testing" -v "2025 R1" --url "https://test-jms.awsansys11np.onscale.com/hps" --num-jobs=1 --account=onprem_account --token=%TOKEN%
REM python project_setup.py --urls "https://test-jms.awsansys11np.onscale.com/hps" "https://dev-jms.awsansys11np.onscale.com/hps"  --accounts "onprem_account" "30b226d7-aa1b-4001-b763-f88525abde4d" --token=%TOKEN%
python project_setup.py --urls "https://dev-jms.awsansys11np.onscale.com/hps"  --accounts "onprem_account" "30b226d7-aa1b-4001-b763-f88525abde4d" "0fea8f1b-0f0f-4998-938a-37a62db59481" --token=%TOKEN%

pause