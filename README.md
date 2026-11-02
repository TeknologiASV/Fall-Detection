## mmWave people counting

This repository ueses 

# Install

```shell
sh setup.sh
```

# Run

- for radar data acquisition

```shell
python3 main_radar.py 
```

- for radar data processing

```shell
python3 main.py
```

# crontab

- run radar data acquisition

```shell
@reboot (cd home/pi/one_u && nohub python3 main_radar.py)
```

- run data processing

```shell
@reboot (cd home/pi/one_u && nohub python3 main.py) >> home/pi/one_u/log/log.log 2>&1
```
