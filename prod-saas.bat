cd dev_env
cd Scripts
call activate.bat
cd ..
cd ..

REM python -m pip install "ansys-rep-common @ git+https://github.com/ansys-internal/rep-common-py.git@main#egg=ansys-rep-common"

set BASE_PROD_URL=https://hps.ansys.com/hps
set BASE_URL=https://dev-jms.awsansys11np.onscale.com/hps
set ACCOUNT_BURST=30b226d7-aa1b-4001-b763-f88525abde4d
set ACCOUNT_BURST_2=72670e8c-43fe-4ec3-bcf8-20be821d91c1
set ACCOUNT_TOASTER=0fea8f1b-0f0f-4998-938a-37a62db59481
set ACCOUNT_PROD=e8cfbf84-058c-43cf-9eb4-9917b1ab2e9f

REM for /f "delims=" %%a in ('python oidc_pkce.py -u %BASE_URL%') do @set TOKEN=%%a
for /f "delims=" %%a in ('python oidc_pkce.py -u %BASE_PROD_URL%') do @set TOKEN_PROD=%%a

REM python examples/generic_api/project_setup.py --urls "%BASE_URL%"  --accounts "%ACCOUNT%" --token=%TOKEN%
python examples/mapdl_tyre_performance/project_setup.py --name "Burst Account tests" -v "2025 R1" --use-exec-script True --url "%BASE_PROD_URL%" --num-jobs=1 --account="%ACCOUNT_PROD%" --token=%TOKEN_PROD%
REM python examples/mapdl_tyre_performance/project_setup.py --name "Burst Account tests jon" -v "2025 R1" --use-exec-script True --url "%BASE_URL%" --num-jobs=1 --account="%ACCOUNT_BURST%" --token=%TOKEN%
REM python examples/generic_api/project_setup.py --urls "%BASE_URL%"  --accounts "%ACCOUNT%" --token=%TOKEN%
REM python project_setup.py --urls "%BASE_URL%" --accounts "onprem_account" --token=%TOKEN% REM --verbose=True
REM python project_setup.py --urls "%BASE_URL%"  --accounts "30b226d7-aa1b-4001-b763-f88525abde4d" "0fea8f1b-0f0f-4998-938a-37a62db59481" --token=%TOKEN%

pause