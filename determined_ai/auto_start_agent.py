import sys
import os
import json
import yaml
import socket
from gpuServiceHelper import getAvalibleGpuList
import time
hostname = socket.gethostname()

if __name__ =="__main__":
    # 每个GPU至少有多少内存才会将其列入可用的GPUlist
    min_mem = 8000
    
    avalible_gpus = getAvalibleGpuList(min_mem)
    print("满足最低内存{}Mb的可用gpu有{}".format(min_mem,avalible_gpus))
    # 每个代理 分配一个GPU
    for i,gpu in enumerate(avalible_gpus ):
        with open("./agent.yaml","r",encoding="utf-8") as f:
            config_dict = yaml.full_load(f)
            print(config_dict.keys())
            config_dict['visible_gpus'] = gpu
            config_dict["agent_id"] = hostname+"_"+gpu
        with open("./agent.yaml","w",encoding="utf-8") as f:
            print(config_dict)
            yaml.dump(config_dict,f)
            command_strs = """nohup docker run --gpus all \
    --network host --name determined-agent-{} \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v "$PWD"/agent.yaml:/etc/determined/agent.yaml \
    determinedai/determined-agent:0.17.2 \
    run --master-port=8080 >/dev/null 2>&1 &
""".format(i)
        print(command_strs)
        os.system(command_strs)

        time.sleep(5)
        
        print("当前配置文件:{}".format(config_dict))
# 服务停止的命令如下
#docker stop $(docker ps -a | grep determined-agent:0.17.2|awk '{print $1}')
#docker rm $(docker ps -a | grep determined-agent:0.17.2|awk '{print $1}')
