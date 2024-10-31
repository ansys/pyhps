cd dev_env
cd Scripts
call activate.bat
cd ..
cd ..


REM python -m pip install "ansys-rep-common @ git+https://github.com/ansys-internal/rep-common-py.git@main#egg=ansys-rep-common"

set BASE_URL=https://dev-jms.awsansys11np.onscale.com/hps
set BASE_PROD_URL=https://hps.ansys.com/hps
REM set BASE_URL=https://10.231.106.121:3000/hps
REM set BASE_URL=https://test-jms.awsansys11np.onscale.com/hps
set ACCOUNT_BURST=30b226d7-aa1b-4001-b763-f88525abde4d
set ACCOUNT_TOASTER=0fea8f1b-0f0f-4998-938a-37a62db59481
set ACCOUNT_PROD=e8cfbf84-058c-43cf-9eb4-9917b1ab2e9f

REM for /f "delims=" %%a in ('python oidc_pkce.py -u %BASE_URL%') do @set TOKEN=%%a
for /f "delims=" %%a in ('python oidc_pkce.py -u %BASE_PROD_URL%') do @set TOKEN_PROD=%%a

REM When connecting to SaaS
python examples/generic_api/project_setup.py --urls "%BASE_PROD_URL%" --token=%TOKEN_PROD% --accounts "%ACCOUNT_PROD%" --verbose=true --signing_key="D:/ansysDev/signing_prod.key"
python examples/generic_api/project_setup.py --urls "%BASE_PROD_URL%" --token=%TOKEN_PROD% --limited_monitor True --remove=old --signing_key="D:/ansysDev/signing_prod.key"

REM python examples/generic_api/project_setup.py --urls "%BASE_URL%"  --token=%TOKEN% --accounts "%ACCOUNT_BURST%" "%ACCOUNT_TOASTER%" --verbose=true --monitor True --remove=old --signing_key="D:/ansysDev/signing.key"
REM python examples/generic_api/project_setup.py --urls "%BASE_URL%" --token=%TOKEN% --accounts "%ACCOUNT_BURST%" "%ACCOUNT_TOASTER%" --monitor True --remove=any --signing_key="D:/ansysDev/signing.key"

REM When connecting to a pcluster
REM python examples/generic_api/project_setup.py --urls "%BASE_URL%"  --username=repadmin --password=repadmin --verbose=true
REM python examples/generic_api/project_setup.py --urls "%BASE_URL%"  --username=repadmin --monitor True --signing_key="D:/ansysDev/pcluster_signing.key" --skip_verify


REM --remove=old
REM --filter=linear 
REM --signing_key="D:/ansysDev/signing.key"
REM --project "New New Tests"

pause