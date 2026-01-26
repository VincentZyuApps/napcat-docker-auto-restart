## 直接用wscat
```shell
npm install -g wscat
wscat -c ws://192.168.31.233:3000?access_token=test
# send this:
# {"action": "get_login_info", "params": {}, "echo": "123"}
```

### result:
```log
(venv) PS G:\GGames\Minecraft\shuyeyun> wscat -c ws://192.168.31.233:3000?access_token=test
Connected (press CTRL+C to quit)
< {"time":1769406187,"self_id":3967912008,"post_type":"meta_event","meta_event_type":"lifecycle","sub_type":"connect"}
> {"action": "get_login_info", "params": {}, "echo": "123"}
< {"status":"ok","retcode":0,"data":{"user_id":3967912008,"nickname":"🤖-dev-bot-"},"message":"","wording":"","echo":"123","stream":"normal-action"}
>
(venv) PS G:\GGames\Minecraft\shuyeyun> 
```

## 或者用node运行js脚本
```shell
cd js
# cd G:\GGames\Minecraft\shuyeyun\qq-bot\napcat-docker-auto-restart\js
npm init -y
npm install ws
```