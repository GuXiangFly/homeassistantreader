## 一个能将 homeassistant 的 sensor同步到  postgresql，并且使用grafana 展示的软件



### 构建docker镜像 
```bash
 docker build -t homeassistantreader .
```



### 启动 homeassistantreader
```bash
  docker run -d  --name ha-reader --restart unless-stopped -v $(pwd)/logs:/app/logs homeassistantreader
```