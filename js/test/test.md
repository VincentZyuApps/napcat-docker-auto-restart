## 直接用wscat
```shell
npm install -g wscat
wscat -c ws://192.168.31.51:13000?access_token=dev
# send this:
# {"action": "get_login_info", "params": {}, "echo": "123"}
```

### result:
```log
(venv) PS G:\GGames\Minecraft\shuyeyun> wscat -c ws://192.168.31.51:13000?access_token=dev
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

node .\test\test_get_login_info.js
node .\test\test_get_status.js   
```

两个脚本都支持通过 `--url` 指定 NapCat WebSocket 地址；不传时默认使用
`ws://192.168.31.51:13000?access_token=dev`。

```powershell
# 传入单独的参数值
node .\test\test_get_login_info.js --url "ws://127.0.0.1:3000?access_token=your_token"
node .\test\test_get_status.js --url "ws://127.0.0.1:3000?access_token=your_token"

# 等号形式同样支持
node .\test\test_get_status.js --url="wss://napcat.example.com?access_token=your_token"

# 通过 package.json 中的 npm scripts 运行时，需要用 -- 转发参数
npm run test:login -- --url "ws://127.0.0.1:3000?access_token=your_token"
npm run test:status -- --url "ws://127.0.0.1:3000?access_token=your_token"

```
