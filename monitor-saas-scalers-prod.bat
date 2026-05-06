cd dev_env
cd Scripts
call activate.bat
cd ..
cd ..


REM python -m pip install "ansys-rep-common @ git+https://github.com/ansys-internal/rep-common-py.git@main#egg=ansys-rep-common"

set BASE_PROD_URL=https://hps.ansys.com/hps

set ACCOUNT_PROD=e8cfbf84-058c-43cf-9eb4-9917b1ab2e9f

for /f "delims=" %%a in ('python oidc_pkce.py -u %BASE_PROD_URL%') do @set TOKEN_PROD=%%a

REM When connecting to SaaS
for /f "delims=" %%b in ('python create_self_signed_token.py --signing_key="D:/ansysDev/signing_prod.key" --token=%TOKEN_PROD%') do @set SELF_TOKEN=%%b

REM When connecting to SaaS
python examples/generic_api/test_rms.py --urls "%BASE_PROD_URL%" --token=%SELF_TOKEN%
REM --filter=linear 


pause