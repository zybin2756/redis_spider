import re

pattern = r".*?经验((\d+-\d+)|(\d+))年.*"
value ="""
                    8k-15k 
                    /广州 /
                    经验10年 /
                    本科及以上 /
                    全职
                
                
                
                                    
                2016-10-16  发布于拉勾网
"""
match_obj = re.match(pattern, value, re.DOTALL)

if match_obj:
    print(match_obj.group(1))