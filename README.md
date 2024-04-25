# RAISA WEB 

## Dependencies 
Install dependencies
```
pip install flask
pip install flask_jwt_extended
pip install waitress
pip install selenium
```

## Install 
```
mkdir -p ${HOME}/.config/systemd/user 
cp raisa-web.service ${HOME}/.config/systemd/user/raisa-web.service
systemctl --user daemon-reload
systemctl --user enable raisa-web.service # untuk auto-start
```

## Run and Stop 
```
systemctl --user start raisa-web.service # Untuk start web 
systemctl --user stop raisa-web.service # untuk stop
```

## Ingat 
Jangan lupa untuk menetapkan env var UI_ASSETS pada raisa-web.service   
Web bisa diakses di port 65500

## MISC 
### Install Update Cuaca
```
mkdir -p ${HOME}/.config/systemd/user 
cp update-cuaca.* ${HOME}/.config/systemd/user/.
systemctl --user daemon-reload
```

### Run cronjob-like Update Cuaca 
```
systemctl --user start update-cuaca.timer
```

### Install Get Internet ITS 
```
mkdir -p ${HOME}/.config/systemd/user 
cp get_internet_its.service ${HOME}/.config/systemd/user/.
systemctl --user daemon-reload
```

### Run 
```
systemcel --user start get_internet_its.service
```

### Peringatan untuk Get Internet ITS 
Pastikan executable browser nya pada get_internet_accessv2.py biasanya menggunakan google-chrome atau chromium untuk mendapatkan path nya bisa melakukan `which google-chrome`



## NOTES 
Untuk install semua cukup gunakan command 
```
mkdir -p ${HOME}/.config/systemd/user 
cp *.service ${HOME}/.config/systemd/user/.
cp *.timer ${HOME}/.config/systemd/user/.
systemctl --user daemon-reload
```