cd dev_env
cd Scripts
call activate.bat
cd ..
cd ..

REM python -m pip install "ansys-rep-common @ git+https://github.com/ansys-internal/rep-common-py.git@main#egg=ansys-rep-common"

REM set TOKEN=eyJhbGciOiJSUzI1NiIsImtpZCI6ImNWQWZMRlQyZS1qT1A2QmlmOUxvRGRRaC1kdC1sazlpa2Fab0EzY0U2bWsiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiI3YTBjNzUxNy1lNzdlLTQ3MDItOGU2MC0zYTg3ZGFmM2EwY2MiLCJpc3MiOiJodHRwczovL2EzNjVkZXYuYjJjbG9naW4uY29tL2NhNGZmNDVhLTI3MzMtNDBkNS1hNGIyLTNjMGYzMDhiYWM5MS92Mi4wLyIsImV4cCI6MTczMDIxODQyNSwibmJmIjoxNzMwMjE0ODI1LCJlbWFpbCI6Impvbi5ub3Zha0BhbnN5cy5jb20iLCJzdWIiOiJmZDUyZTc1ZC1mNzJlLTQyMTItYTczYy00ZjY3NGI5NWExZjciLCJVSUQiOiJmZDUyZTc1ZC1mNzJlLTQyMTItYTczYy00ZjY3NGI5NWExZjciLCJ0aWQiOiIzNGM2Y2U2Ny0xNWI4LTRlZmYtODBlOS01MmRhOGJlODk3MDYiLCJnaXZlbl9uYW1lIjoiSm9uIiwiZmFtaWx5X25hbWUiOiJOb3ZhayIsIm5hbWUiOiJKb24gTm92YWsiLCJub25jZSI6IlkyaGFkRE55TVcxS1VYQmZSV1ZCY1ZsNFJrTnZiREpVZDJ0dmVUUnhZVnBLZUc1dWVtVnJVVEU1ZGpCciIsImF6cCI6IjdhMGM3NTE3LWU3N2UtNDcwMi04ZTYwLTNhODdkYWYzYTBjYyIsInZlciI6IjEuMCIsImlhdCI6MTczMDIxNDgyNX0.FlaWMcjSRmCgDxcTMMN2G6LtVF8hL-jmdjYNRPuh32nHp2woPpG-halDfaeZPlIQhUdKLVKwb-Zqtir3epiazzl71kzrKeV5XREn7MOZrV79C1aVQRJTl-r1mHGbTi5DzcMDIskalYFpxgAbr-nKJK9WRqgPBpq7F8bH9hhyulXSgRZTOVI-e29WfCM3DFXHnxtDYEihkqpWq_arywquz7LqL_u6EpEZbrCsv26utSdJkyLrCAwefBI0Y7VDZfkqxKkgk17q5b1yo_15Y-Y7u54INgXLj44LrS_qczFuLQz5RmvixSWWxWp-zSOP3mJPKV2za2XWlJSpNLtjB-VJOg
set BASE_URL=https://dev-jms.awsansys11np.onscale.com/hps
set BASE_PROD_URL=https://hps.ansys.com/hps
REM set BASE_URL=https://10.231.106.121:3000/hps
REM set BASE_URL=https://test-jms.awsansys11np.onscale.com/hps
set ACCOUNT_BURST=30b226d7-aa1b-4001-b763-f88525abde4d
set ACCOUNT_TOASTER=0fea8f1b-0f0f-4998-938a-37a62db59481
set ACCOUNT_PROD=e8cfbf84-058c-43cf-9eb4-9917b1ab2e9f

REM for /f "delims=" %%a in ('python oidc_pkce.py -u %BASE_URL%') do @set TOKEN=%%a
for /f "delims=" %%a in ('python oidc_pkce.py -u %BASE_PROD_URL%') do @set TOKEN_PROD=%%a


REM python examples/generic_api/project_setup.py --urls "%BASE_URL%"  --accounts "%ACCOUNT%" --token=%TOKEN%
python examples/mapdl_tyre_performance/project_setup.py --name "Burst Account tests" -v "2025 R1" --use-exec-script True --url "%BASE_PROD_URL%" --num-jobs=1 --account="%ACCOUNT_PROD%" --token=%TOKEN_PROD%
REM python examples/mapdl_tyre_performance/project_setup.py --name "Burst Account tests" -v "2025 R1" --use-exec-script True --url "%BASE_URL%" --num-jobs=1 --account="%ACCOUNT%" --token=%TOKEN%
REM python examples/generic_api/project_setup.py --urls "%BASE_URL%"  --accounts "%ACCOUNT%" --token=%TOKEN%
REM python project_setup.py --urls "%BASE_URL%" --accounts "onprem_account" --token=%TOKEN% REM --verbose=True
REM python project_setup.py --urls "%BASE_URL%"  --accounts "30b226d7-aa1b-4001-b763-f88525abde4d" "0fea8f1b-0f0f-4998-938a-37a62db59481" --token=%TOKEN%

pause