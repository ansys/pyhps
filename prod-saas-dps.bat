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
set ACCOUNT_PROD_TESTING=ddb9143e-5916-41e7-8f4f-76dd0f32e7f6

REM for /f "delims=" %%a in ('python oidc_pkce.py -u %BASE_URL%') do @set TOKEN=%%a
for /f "delims=" %%a in ('python oidc_pkce.py -u %BASE_PROD_URL%') do @set TOKEN_PROD=%%a

echo %TOKEN_PROD%
REM ping 127.0.0.1 -n 10

REM python examples/mapdl_tyre_performance/project_setup.py --name "Burst Account tests" -v "2025 R2" --use-exec-script True --url "%BASE_PROD_URL%" --num-jobs=1 --account="%ACCOUNT_PROD%" --token=%TOKEN_PROD%
REM python examples/mapdl_motorbike_frame/project_setup.py --name "Burst account test" -v "2025 R2" --use-exec-script --url "%BASE_PROD_URL%" --num-jobs=2 --account="%ACCOUNT_PROD%" --token=%TOKEN_PROD%
python examples/mapdl_motorbike_frame/project_setup.py --name "DP TESTING JON 5" -v "2025 R2" --use-exec-script --url "%BASE_PROD_URL%" --account="%ACCOUNT_PROD%" --num-jobs=5 --token=%TOKEN_PROD%

pause