cd dev_env
cd Scripts
call activate.bat
cd ..
cd ..

set TOKEN=eyJhbGciOiJSUzI1NiIsImtpZCI6ImNWQWZMRlQyZS1qT1A2QmlmOUxvRGRRaC1kdC1sazlpa2Fab0EzY0U2bWsiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJkY2UyNjc3My03NTZkLTQ2NzEtYjJlNC05ZTEyZmZlZDA3ZjYiLCJpc3MiOiJodHRwczovL2EzNjVkZXYuYjJjbG9naW4uY29tL2NhNGZmNDVhLTI3MzMtNDBkNS1hNGIyLTNjMGYzMDhiYWM5MS92Mi4wLyIsImV4cCI6MTcyODA2MjMyMSwibmJmIjoxNzI4MDU4NzIxLCJzdWIiOiJmZDUyZTc1ZC1mNzJlLTQyMTItYTczYy00ZjY3NGI5NWExZjciLCJlbWFpbCI6Impvbi5ub3Zha0BhbnN5cy5jb20iLCJ0aWQiOiIzNGM2Y2U2Ny0xNWI4LTRlZmYtODBlOS01MmRhOGJlODk3MDYiLCJnaXZlbl9uYW1lIjoiSm9uIiwiZmFtaWx5X25hbWUiOiJOb3ZhayIsIm5hbWUiOiJKb24gTm92YWsiLCJVSUQiOiJmZDUyZTc1ZC1mNzJlLTQyMTItYTczYy00ZjY3NGI5NWExZjciLCJub25jZSI6IlZqQXdXRnBQZWpOb1QwNXJNbGx1YlVoSmR6TXdSV2RVUVRaQlMwWkhjVzltUjJKSGNFdHNNa3hHVnpndSIsInNjcCI6IkxpY2Vuc2luZ0FzQVNlcnZpY2UiLCJhenAiOiIwMDgzNWJjZC00MjQ1LTRkNjEtOTE5Yy1jYzhjMzdkYjdkN2YiLCJ2ZXIiOiIxLjAiLCJpYXQiOjE3MjgwNTg3MjF9.OtejtDdSg4JFA4sNUYZdjje69IQ3pbI4C0WevR6KBIH0Vfz7b74-_fxOQz_9Wkr0g4T3hi8Ve4Fv178Gw3AlLl35wyG7ovZzb_CgvwxvgNSEMcKiRJuxuub1wOxfDyxD_iI4atBfFnDoeqexompJREiKKWXidmabCEmZdmz_HhBTEL1lnTFIn63c96Ycjs1o3bD2wjusA3CT4YYPRjxH0JnwRR-TnFiV1PPclweaL63SDkKIxNi6_C-qgPlAeUYhYKz5iwAwtjTuv7bOZh6Mlflur9VA93orujP1uX5Lf78T_RZehvksKgaPNavJcpbXkJZmTjPkxdJB6Iqaj2rbxA

python examples/generic_api/project_setup.py --urls "https://dev-jms.awsansys11np.onscale.com/hps"  --accounts "0fea8f1b-0f0f-4998-938a-37a62db59481" --token=%TOKEN%
python examples/mapdl_tyre_performance/project_setup.py --name "New New tests" -v "2025 R1" --url "https://dev-jms.awsansys11np.onscale.com/hps" --num-jobs=1 --account="0fea8f1b-0f0f-4998-938a-37a62db59481" --token=%TOKEN%
python examples/generic_api/project_setup.py --urls "https://dev-jms.awsansys11np.onscale.com/hps"  --accounts "0fea8f1b-0f0f-4998-938a-37a62db59481" --token=%TOKEN%
REM python project_setup.py --urls "https://test-jms.awsansys11np.onscale.com/hps" --accounts "onprem_account" --token=%TOKEN% REM --verbose=True
REM python project_setup.py --urls "https://dev-jms.awsansys11np.onscale.com/hps"  --accounts "30b226d7-aa1b-4001-b763-f88525abde4d" "0fea8f1b-0f0f-4998-938a-37a62db59481" --token=%TOKEN%

pause