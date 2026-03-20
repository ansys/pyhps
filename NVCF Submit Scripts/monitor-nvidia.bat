cd ..
cd dev_env
cd Scripts
call activate.bat
cd ..
cd ..


set BASE_URL=https://test-jms.awsansys11np.onscale.com/hps

set ACCOUNT_TOASTER=0fea8f1b-0f0f-4998-938a-37a62db59481

for /f "delims=" %%a in ('python oidc_pkce.py -u %BASE_URL%') do @set TOKEN=%%a

python examples/generic_api/project_setup.py --urls "%BASE_URL%"  --token=%TOKEN% --signing_key="D:/ansysDev/signing.key"
python examples/generic_api/project_setup.py --urls "%BASE_URL%"  --token=%TOKEN% --accounts "%ACCOUNT_TOASTER%" --remove=quick --verbose=true --monitor True --signing_key="D:/ansysDev/signing.key"

pause