cd dev_env
cd Scripts
call activate.bat
cd ..
cd ..


set BASE_URL=https://dev-jms.awsansys11np.onscale.com/hps
set ACCOUNT_BURST=30b226d7-aa1b-4001-b763-f88525abde4d
set ACCOUNT_TOASTER=0fea8f1b-0f0f-4998-938a-37a62db59481


for /f "delims=" %%a in ('python oidc_pkce.py -u %BASE_URL%') do @set TOKEN=%%a

for /f "delims=" %%b in ('python create_self_signed_token.py --signing_key="D:/ansysDev/signing.key" --token=%TOKEN%') do @set SELF_TOKEN=%%b

REM When connecting to SaaS
python examples/generic_api/test_rms.py --urls "%BASE_URL%" --token=%SELF_TOKEN%
REM --filter=becd2b05


pause