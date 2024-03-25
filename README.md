# RAISA WEB 

## Dependencies 
Install dependencies
```
pip install flask
pip install flask_jwt_extended
pip install waitress
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

