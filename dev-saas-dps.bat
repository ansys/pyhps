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
set ACCOUNT_ANYWHERE=becd2b05-9e2b-4325-bc57-ab0225d6b5b5

for /f "delims=" %%a in ('python oidc_pkce.py -u %BASE_URL%') do @set TOKEN=%%a
REM for /f "delims=" %%a in ('python oidc_pkce.py -u %BASE_PROD_URL%') do @set TOKEN_PROD=%%a

echo %TOKEN%

REM python examples/generic_api/project_setup.py --urls "%BASE_URL%"  --accounts "%ACCOUNT%" --token=%TOKEN%
python examples/mapdl_motorbike_frame/project_setup.py --name "DP TESTING JON 50" -v "2025 R2" --use-exec-script --url "%BASE_URL%" --num-jobs=50 --one-to-one --account="%ACCOUNT_BURST%" --token=%TOKEN%
REM python examples/generic_api/project_setup.py --urls "%BASE_URL%"  --accounts "%ACCOUNT%" --token=%TOKEN%
REM python project_setup.py --urls "%BASE_URL%" --accounts "onprem_account" --token=%TOKEN% REM --verbose=True
REM python project_setup.py --urls "%BASE_URL%"  --accounts "30b226d7-aa1b-4001-b763-f88525abde4d" "0fea8f1b-0f0f-4998-938a-37a62db59481" --token=%TOKEN%

pause