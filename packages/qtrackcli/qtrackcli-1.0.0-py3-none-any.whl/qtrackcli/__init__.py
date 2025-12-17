__version__ = "0.1.0"
"""使用python调用接口http://localhost:8080/pytest_xml_automation,
并编写成第三方库qtrackcli，上传到PyPI,请给出完整代码， 
调用命令如下： 
pip install qtrackcli 
qtrackcli -y 
-h "https://localhost:8080" 
-u "USER_EMAIL" 
-p "API_TOKEN" 
--project "PROJECT NAME" 
parse_junit --title "Automated Test Run" 
--run-description "CI Build" 
-f "reports/junit-report.xml"""