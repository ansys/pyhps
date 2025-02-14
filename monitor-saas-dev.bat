cd dev_env
cd Scripts
call activate.bat
cd ..
cd ..


set BASE_URL=https://dev-jms.awsansys11np.onscale.com/hps
set ACCOUNT_BURST=30b226d7-aa1b-4001-b763-f88525abde4d
set ACCOUNT_TOASTER=0fea8f1b-0f0f-4998-938a-37a62db59481


for /f "delims=" %%a in ('python oidc_pkce.py -u %BASE_URL%') do @set TOKEN=%%a

REM When connecting to SaaS
python examples/generic_api/project_setup.py --urls "%BASE_URL%"  --token=%TOKEN% --accounts "%ACCOUNT_BURST%" --verbose=true --signing_key="D:/ansysDev/signing.key"
python examples/generic_api/project_setup.py --urls "%BASE_URL%"  --token=%TOKEN% --verbose=true --monitor True --signing_key="D:/ansysDev/signing.key"
REM --limited_monitor True

REM --remove=old
REM --filter=linear 
REM --signing_key="D:/ansysDev/signing.key"
REM --project "New New Tests"

pause