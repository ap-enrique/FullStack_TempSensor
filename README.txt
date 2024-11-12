Här är en steg-för-steg-guide för att installera, konfigurera och implementera en säker IoT-lösning med Raspberry Pi, temperatursensor, MQTT över TLS, InfluxDB och Grafana.

Översikt:
Raspberry Pi: Kommer att läsa data från en temperatursensor och fungera som MQTT-klient och broker för att skicka data till en laptop.
Laptop (Windows 11): Kör InfluxDB och Grafana för att lagra och visualisera data.
Mobil Hotspot: Används för att skapa ett nätverk som både din Raspberry Pi och laptop kan ansluta till för kommunikation.

Förberedelser:
En Raspberry Pi (med Raspbian installerat).
En DHT11/DHT22 temperatursensor.
En mobil hotspot för nätverk.
Din Windows Laptop för visualisering.

1. Installera och Konfigurera på Raspberry Pi
1.1 Installera Raspbian OS
1.2 Starta raspberry och kör:
	sudo apt-get update
	sudo apt-get upgrade
1.3 Aktivera SSH för fjärråtkomst på Raspberry Pi:
	sudo raspi-config
	Gå till Interface Options > SSH > Enable
1.4 Anslut till mobil hotspot på Raspberry Pi:
	sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
	
	network={
    		ssid="Namn på Hotspot"
    		psk="Lösenord för hotspot"
	}
1.5 Kontrollera Pi IP-adress på Raspberry Pi:
	sudo hostname -I
1.6 Nu kan en ansluta sig till Raspberry Pi via SSH från laptop terminal eller shell:
	ssh <användarnamn>@<Raspberry Pi IP-adress eller enhetens namn>
	ssh admin@rpi-4
	ssh admin@xxx.xxx.xxx


2. Installera Mosquitto Broker (MQTT Broker är som en “central station” som tar emot och vidarebefordrar meddelanden mellan enheter på Raspberry Pi)
2.1 Installera Mosquitto och client verktyg på Raspberry Pi
	sudo apt-get install mosquitto mosquitto-clients
2.2 Installera Mosquitto paho-mqtt
	sudo apt-get isntall paho-mqtt
2.3 konfigurera /etc/mosquitto/mosquitto.conf
	listener 1883
	allow_anonymous true
2.3 Starta och aktivera Mosquitto: För att Mosquitto ska starta automatiskt när din Pi startar
	sudo systemctl start mosquitto
	sudo systemctl enable mosquitto
	sudo systemctl status mosquitto
2.4 Skriv python script som innehållet sensor Reading och sänder data till mqtt brokern för publicering av topic.


3. Lokalt testning på Raspberry Pi
3.1 På en terminal subscribe
	mosquitto_sub -h <raspberry pi ip> -t <topic>
3.2 På ett annat terminal start python script eller från IDE
	python3 <path-filname>.py
3.3 Du kommer se hur data registreras på både script fönster och subscriber fönster
3.4 Skriv en annan python som subscriber topic från sensor och därefter skickar iväg det till influxdb.


4. Installera och konfigurera Influxdb-container på Windows laptop
4.1 Öppna File Explorer och skapa en mapp där InfluxDB kan spara sin data. Ex: skapa en mapp på C:\Users\apenr\OneDrive\Nackademin\Datorkommunikation\PROJEKT\influxdb-data. Detta gör att data sparas även om containern tas bort.
4.1 Från CMD eller PowerShell i windows ladda InfluxDB
	docker run -d -p 8086:8086 --name=influxdb `
		-v C:\Users\apenr\OneDrive\Nackademin\Datorkommunikation\PROJEKT\influxdb-data:/var/lib/influxdb2 `
		-e DOCKER_INFLUXDB_INIT_MODE=setup `
		-e DOCKER_INFLUXDB_INIT_USERNAME=admin `
		-e DOCKER_INFLUXDB_INIT_PASSWORD=password `
		-e DOCKER_INFLUXDB_INIT_ORG=nackademin `
		-e DOCKER_INFLUXDB_INIT_BUCKET=sensor-temp `
		influxdb:2.0

	docker start influxdb-temmpSensor
4.2 Håll det enkelt för praktik. Org ska vara enkelt också. Bucket är egentligen namn för databas i influxdb språk.
	docker run -d: Startar en container i bakgrunden.
	-p 8086:8086: Kopplar port 8086 på din dator till port 8086 i containern, vilket gör att du kan komma åt InfluxDB via den porten.
	-v C:\<FULL PATH>\influxdb-data:/var/lib/influxdb2: Kopplar mappen du skapade till InfluxDB datamapp i containern.
	-e DOCKER_INFLUXDB_INIT_*: Dessa är miljövariabler som behövs för att konfigurera InfluxDB när containern startas första gången:
	DOCKER_INFLUXDB_INIT_USERNAME=admin: Skapar en användare med användarnamn admin.
	DOCKER_INFLUXDB_INIT_PASSWORD=password: Lösenordet för användaren admin.
	DOCKER_INFLUXDB_INIT_ORG=nackademin: Namnet på organisationen i InfluxDB.
	DOCKER_INFLUXDB_INIT_BUCKET=sensor-temp: Namnet på den databas ("bucket") där vi kommer lagra data.

	docker start grafana-tempSensor
4.3 Kontrollera att influxDB körs. Använd samma kommando:
	docker ps
4.4 Öppna InfluxDB i webbläsaren på Windows laptop
	Öppna webbläsare och gå till: http://localhost:8086. Här kan du logga in med användarnamn admin och lösenord password
4.5 Gå till huvudmenyn vänster spalt. Gå till Data. Gå till Buckets. Trycke på din egen skapad bucket "sensor-temp". Det kommer ta dig till Data Explorer
4.6 Query:
	Spalten from välje: sensor-temp
	Spalten Filter välje: _measurement och byt till sensor
	Spalten Filter from sensor: Välje din sensor som du vill mäta. Humidity eller Temperatur eller båda samtidigt.
	Spalten Filter from det förra val välje: temperature_sensor
4.7 Sedan tryck på knappen Script Editor och scriptet ska användas för Grafana.
4.8 Gå till huvudmenyn vänster spalten. Gå till Tokens.
	Tryck +Generate Token
	Välj all access token
	Skriv ett namn för token
	Spara
4.9 Token används för Grafana


5. MQTT Brokern Publicering och sända data till InfluxDB
5.1 Starta python script för sensor som publicerar mqtt meddelande
5.2 Starta python script för att sända j-son meddelande till influxdb


6. Installera och konfigurera Grafana-container på Windows laptop
6.1 Skapa en mapp för Grafana-data. Precis som för InfluxDB, skapa en mapp på C:\ för att spara Grafana-data, t.ex. C:\Users\apenr\OneDrive\Nackademin\Datorkommunikation\PROJEKT\grafana-data.
6.2 Starta en Grafana-container. I samma kommandoprompt eller PowerShell, kör följande kommando för att skapa och starta en Grafana-container:
	docker run -d -p 3000:3000 --name=grafana `
	-v C:\grafana-data:/var/lib/grafana `
	grafana/grafana
6.3 Förklaring
	-p 3000:3000: Kopplar port 3000 på din dator till port 3000 i Grafana-containern.
	-v C:\Users\apenr\OneDrive\Nackademin\Datorkommunikation\PROJEKT\grafana-data:/var/lib/grafana: Mappen där Grafana sparar sin data.
6.4 Kontrollera att Grafana körs. Använd samma kommando som tidigare:
	docker ps
6.5 Öppna Grafana i webbläsaren. Gå till http://localhost:3000 i webbläsaren.
6.6 Logga in med standardanvändaren admin och lösenordet admin. Du kommer omedelbart att uppmanas att ändra lösenordet. Ändra till password för praktik.
6.7 I Grafana Home menyn. Vänster spalten. Gå till Data Sources. Tryck på Add new data source.
6.8 För det här övning är det Time Series databases. InfluxDB.
6.9 Konfiguration
	Name = Sensor-Temp-Humdity
	Query Language = Flux
	HTTP/URL = http://192.168.62.7:8086 //Laptops IP adress och port nummer för influxdb
	Auth/Basic Auth
		User = admin
		Password = password //admin lösenord från influxdb 
	InfluxDB Details
		Organization = nackademin
		Token = Eget skapat token från InfluxDB.
		Default Bucket = sensor-temp
		Min time interval = 10
		Max Series = 1000
	Save & Test


7. Skapa en Dashbord i Grafana på Windows laptop
7.1 Gå till Home menyn på vänster spalt. Gå till Dashboards. Tryck New och välj New Dashboard.
7.2 Tryck på + Add visualization
7.3 Select data source = Bucket from influxDB
7.4 Du kan byta namn på Query. Istället för "A" välje en relevant presentation namn för den fönster query.
7.4 Scriptet fråm InfluxDB och klistra den på Grafana Query.
7.5 Ovanför finns time range. Ändra det till Last 15 minutes or 5 minutes.
7.6 Efter egna ändringar för Panelen, tryck på Save Dashboard.
7.7 Ge det en titel namn för dashboard och visualizationer och tryck på save. Tryck på back to dashboard
7.8 Tryck på Add och välj Visualization.
7.9 under fliken Data Source du kan ändra vilken bucket ska bli panel för att övervakas. Kör steg 7.4 till 7.7

8. Configure Mosquitto to Allow WebSocket Connections på Raspberry Pi:
	sudo nano /etc/mosquitto/mosquitto.conf
	
	listener 1883
	protocol mqtt
	allow_anonymous true

	listener 9001
	protocol websockets
8.1 Restart
	sudo systemctl restart mosquito
8.2 Bekräfta att WebSocket-porten är aktiv
	sudo netstat -tuln | grep 9001
	ps aux | grep mosquitto


9. Installera och konfigurera nginx på Raspberry Pi
9.1 Updatera och installation
	sudo apt update
	sudo apt upgrade 
 	sudo apt-get install nginx
9.2 Konfigurera Nginx för att hantera WebSocket-trafik
	sudo nano /etc/nginx/sites-available/default

	server {
		listen 80 default_server;
		listen [::]:80 default_server;

		root /var/www/html;
		index index.html;

		server_name _;

		location / {
			try_files $uri /index.html;
		}

		location /mqtt {
			proxy_pass http://localhost:9001;
			proxy_http_version 1.1;
			proxy_set_header Upgrade $http_upgrade;
			proxy_set_header Connection "upgrade";
		}
	}
9.3 Testa Nginx-konfigurationen och starta om
	sudo nginx -t
	sudo systemctl restart nginx
9.3 Skapa en konfigurationsfil för din IoT-webbplats
	sudo nano /etc/nginx/sites-available/iot-dashboard.conf
	
	server {
		listen 80;
		#nginx ip-address
		server_name 192.168.0.129;

		root /var/www/iot-dashboard;
		index index.html;

		location / {
			#try_files för att dirigera alla förfrågningar till index.html
			try_files $uri /index.html;
		}

		#WebSocket-proxy för mqtt
		location /mqtt {
			proxy_pass http://localhost:9001;
			proxy_http_version 1.1;
			proxy_set_header Upgrade $http_upgrade;
			proxy_set_header Connection "upgrade";
		}
	}
9.4 Skapa webbplatsens mappstruktur
	sudo mkdir -p /var/www/iot-dashboard
9.5 Aktivera konfigurationen om Nginx
	sudo ln -s /etc/nginx/sites-available/iot-dashboard.conf /etc/nginx/sites-enabled/
9.6 Testa Nginx-konfigurationen:
	sudo nginx -t
9.7 Om allt ser bra ut, starta om Nginx:
	sudo systemctl restart nginx
9.8 



10. Installera Node.js 16 och npm på Windows laptop
10.1 Ladda ner den rekommenderade versionen (LTS) för Windows på hemsidan.
	node-v16.20.2-x64.msi
10.2 Installera endast node js.
10.3 verifiera med CMD eller PowerShell Admin
	node -v
	npm -v
10.4 Skapa och navigera till den projekt mapp för den nya React-applikation
	makdir C:\Users\Enrique AP\OneDrive\Nackademin\Datorkommunikation\PROJEKT\React\SensorWebpage
	cd C:\Users\Enrique AP\OneDrive\Nackademin\Datorkommunikation\PROJEKT\React\SensorWebpage
10.5 Skapa en ny React-app
	npx create-react-app iot-dashboard
10.6 Öppna React-projektet i Visual Studio Code
	Gå till File > Open Folder och välj att öpnna mappen iot-dashboard där React-projekt finns
10.7 Öppna en terminal i Visual Studio Code genom att gå till Terminal > New Termina
	npm start
	En webbläsare öppnas automatiskt på http://localhost:3000, där du kan se din React-app
10.8 I terminalen i Visual Studio Code, kör
	npm install mqtt
10.9 Redigera React-applikationen för att hämta och visa sensor data
	Öppna filen src/App.js i din React-applikation och ändra den
10.10 I terminalen i Visual Studio Code, bygga applikationen för produktion, kör
	npm run build
10.11 Överför byggfilerna till Raspberry Pi
	PS C:\Users\Enrique AP> scp -r "C:\Users\Enrique AP\OneDrive\Nackademin\Datorkommunikation\PROJEKT\React\SensorWebpage\iot-dashboard\build" admin@192.168.0.129:/home/admin/Projekt
10.12 Flytta allt innehållet från folder build till /var/www/iot-dashboard
	sudo mv /home/admin/Projekt/build/* /var/www/iot-dashboard/
10.13 Rättigheterna för mappen. Ändra ägande av mappen så att Nginx kan läsa filerna
	sudo chown -R www-data:www-data /var/www/iot-dashboard
	sudo chmod -R 755 /var/www/iot-dashboard
	sudo systemctl restart nginx

11. Testa hemsidan
11.1 Öppna från webbläsaren http:\\192.168.38.89


12. VPN wireguard lokalt-nätverk
12.1 Installera och Konfigurera WireGuard på Raspberry Pi (VPN-server)
	sudo apt update && sudo apt upgrade -y
	sudo apt install wireguard -y
12.2 Starta ett root shell genom att använda:
	sudo -i
12.3 Generera Nyckelpar för WireGuard:
	sudo mkdir /etc/wireguard
	cd /etc/wireguard
	umask 077
	wg genkey | tee server_private.key | wg pubkey > server_public.key
12.4 Visa de genererade nycklarna och spara de i en txt fil för att använda dem senare:
	cat server_private.key
	cat server_public.key
12.5 Konfigurera WireGuard-servern. Skapa en konfigurationsfil för WireGuard:
	sudo nano /etc/wireguard/wg0.conf
	
	[Interface]
	Address = 10.0.0.1/24
	ListenPort = 51820
	PrivateKey = <server_private_key>

	[Peer]
	PublicKey = <client_public_key>
	AllowedIPs = 10.0.0.2/32

	
	Förklaring av Varje Fält i Konfigurationsfilen
	[Interface]
	PrivateKey: Ange klientens privata nyckel som du fick när du genererade nyckelparet i WireGuard-applikationen.
	Address: Sätt den IP-adress som klienten ska använda i VPN-nätverket. I det här exemplet använder vi 10.0.0.2/24, men detta beror på det privata subnät du konfigurerat på din Raspberry Pi.
	DNS: Den DNS-server som klienten ska använda för att översätta domännamn. Google DNS (8.8.8.8) är standard här, men du kan byta till vilken DNS-server du vill.
	[Peer]
	PublicKey: Den publika nyckeln från din Raspberry Pi (WireGuard-server). Denna nyckel måste matcha serverns konfiguration för att kommunikationen ska vara säker.
	Endpoint: Raspberry Pi IP-adress och WireGuard-porten (standard är 51820). Exempelvis 192.168.1.10:51820 om det är din Pi interna IP.
	AllowedIPs: Detta fält anger vilket IP-intervall som klienten ska skicka genom VPN-tunneln. I exemplet har vi satt 10.0.0.0/24, vilket betyder att all trafik till VPN-nätverket går genom tunneln.

	
12.6 Starta och aktivera WireGuard-servern:
	sudo wg-quick up wg0

	Kör följande kommando på din Raspberry Pi för att aktivera WireGuard så att det startar automatiskt vid uppstart:
	sudo systemctl enable wg-quick@wg0
	
	Detta skapar en säker VPN-tunnel mellan enheterna. VPN-anslutningen kan användas för att skicka krypterad IoT-data och för att hantera Raspberry Pi
	system på distans.
12.7 Skapa och Konfigurera WireGuard på Klienten (Laptop)
	Installera WireGuard på Windows. Ladda ner WireGuard-klienten från den officiella webbplatsen.
	wireguard-amd64-0.5.3.msi
12.8 Öppna Wireguard GUI
	Om du använder WireGuard-klienten för Windows, kan du i klientens inställningar välja alternativet att automatiskt ansluta till wg0-konfigurationen när datorn startar.

	Tryck på Add Tunnel > Add Empty tunnel:
	Wireguard gör en conf fil och generera klient public och private key
	Copy down these keys somewhere secure in a txt fil för use for Wireguard server konfiguration.
	
	[Interface]
	PrivateKey = <client_private_key>
	Address = 10.0.0.2/24
	DNS = 8.8.8.8

	[Peer]
	PublicKey = <server_public_key>
	Endpoint = <raspberry_pi_ip>:51820
	AllowedIPs = 10.0.0.0/24
	PersistentKeepalive = 25
	

    Förklaring av Varje Fält i Konfigurationsfilen
	[Interface]
	PrivateKey: Ange klientens privata nyckel som du fick när du genererade nyckelparet i WireGuard-applikationen.
	Address: Sätt den IP-adress som klienten ska använda i VPN-nätverket. I det här exemplet använder vi 10.0.0.2/24, men detta beror på det privata subnät du konfigurerat på din Raspberry Pi.
	DNS: Den DNS-server som klienten ska använda för att översätta domännamn. Google DNS (8.8.8.8) är standard här, men du kan byta till vilken DNS-server du vill.
	[Peer]
	PublicKey: Den publika nyckeln från din Raspberry Pi (WireGuard-server). Denna nyckel måste matcha serverns konfiguration för att kommunikationen ska vara säker.
	Endpoint: Raspberry Pi IP-adress och WireGuard-porten (standard är 51820). Exempelvis 192.168.1.10:51820 om det är din Pi interna IP.
	AllowedIPs: Detta fält anger vilket IP-intervall som klienten ska skicka genom VPN-tunneln. I exemplet har vi satt 10.0.0.0/24, vilket betyder att all trafik till VPN-nätverket går genom tunneln.
12.9 To see live traffic of Wireguard interface (wg0), you can use tcpdump on the Raspberry Pi. First, install it
	sudo apt install tcpdump
	sudo tcpdump -i wg0
12.10 For real-time traffic monitoring on your WireGuard interface (wg0), install iftop
	sudo apt install iftop
	sudo iftop -i wg0
12.11 Ping Test from your laptop medan tcpdump och iftop är påslagen, try pinging the Raspberry Pi’s VPN IP (e.g., 10.0.0.1).
	ping 10.0.0.1
12.12 WireGuard-konfigurationskontroll. Starta om WireGuard-tjänsten på båda enheterna för att säkerställa att konfigurationen är uppdaterad:
	sudo systemctl restart wg-quick@wg0


13. Https säkerhetslösning lokalt-nätverk. För en HTTPS-anslutning mellan Raspberry Pi och laptop utan internet
13.1 Skapa ett självsignerat certifikat på Raspberry Pi:
	sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
	-keyout /etc/ssl/private/nginx-selfsigned.key \
	-out /etc/ssl/certs/nginx-selfsigned.crt \
	-subj "/CN=192.168.38.89" \
	-addext "subjectAltName=IP:192.168.38.89"
13.2 Uppdatera Nginx-konfigurationen för att använda HTTPS:
	sudo nano /etc/nginx/sites-available/iot-dashboard.conf
	
	server {
    		listen 80;
    		server_name 192.168.38.89;

		# Omdirigera HTTP till HTTPS
    		return 301 https://$host$request_uri;
	}

	server {
    		listen 443 ssl;
		# Nginx server IP-addres. Raspberry just nu.
    		server_name 192.168.38.89;
		
		# SSL-certifikat och nyckelfiler
    		ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
    		ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;

		# Rotkatalog för React-applikationen
    		root /var/www/iot-dashboard;
    		index index.html;

    		location / {
        	try_files $uri /index.html;
    		}

    		location /mqtt {
			# Information om mqtt brokern server. Just nu är det Raspberry Pi. 
        		proxy_pass http://192.168.38.89:9001;
        		proxy_http_version 1.1;
        		proxy_set_header Upgrade $http_upgrade;
        		proxy_set_header Connection "upgrade";
			proxy_set_header Host $host;
    		}
	}

	sudo nginx -t
	sudo sytemctl restart nginx
13.3 Aktivera HTTPS-konfigurationen och starta om Nginx:
     HTTPS säkrar all kommunikation mellan servern och webbläsaren. Detta är viktigt för att förhindra avlyssning och manipulering av data när din React-webbapplikation kommunicerar med IoT-enheter.

	sudo ln -s /etc/nginx/sites-available/iot-dashboard-ssl.conf /etc/nginx/sites-enabled/
	sudo nginx -t
	sudo systemctl restart nginx
13.4 Felkontroll i webbläsarkonsolen Goggle Chrome
	Öppna utvecklingsverktygen i webbläsaren (ofta med F12), gå till Konsolen och leta efter fel relaterade till anslutningar, certifikat, eller mixed content-varningar (blandat HTTP och HTTPS-innehåll).
	Rensa cache och testa igen
13.5 Uppdatera WebSocket-URL till wss:// i app.js
	Eftersom du laddar webbplatsen över HTTPS, behöver din WebSocket-anslutning använda wss:// istället för ws://. Uppdatera MQTT WebSocket-URL i din React-app till:
	const client = mqtt.connect('wss://192.168.38.89/mqtt'); // Ändra från 'ws://' till 'wss://'
13.6 Konfigurera Nginx för att stödja wss://
     För att Nginx ska hantera WebSocket över wss://, kontrollera att konfigurationsfilen för iot-dashboard stöder detta.
	sudo -i
	nano /etc/nginx/sites-available/iot-dashboard.conf

	server {
    		listen 443 ssl;
    		server_name 192.168.38.89;

    		ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
    		ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;

    		location / {
        		proxy_pass http://localhost:3000; # React frontend
        		proxy_set_header Host $host;
        		proxy_set_header X-Real-IP $remote_addr;
        		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        		proxy_set_header X-Forwarded-Proto $scheme;
    		}

    		location /mqtt {
        		proxy_pass http://192.168.38.89:1883; # Din MQTT-broker
        		proxy_http_version 1.1;
        		proxy_set_header Upgrade $http_upgrade;
        		proxy_set_header Connection "Upgrade";
        		proxy_set_header Host $host;
    		}
	}
13.7 Starta om Nginx för att aktivera den nya konfigurationen:
	sudo -i
	nginx -t
	systemctl restart nginx

INGEN MQTT Via WebSocket eftersom det körs redan med VPN wireguard

14. Uppdatering för MQTT via WebSocket (TLS-säkerhet).
	För att säkerställa att MQTT använder en säker anslutning (MQTTS över WebSocket), kan du konfigurera Mosquitto för TLS genom att generera ett certifikat och sedan ange detta i Mosquitto-konfigurationen.
14.1 Generera ett SSL-certifikat för Mosquitto:
	sudo -i
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
	-keyout /etc/ssl/private/mosquitto-selfsigned.key \
	-out /etc/ssl/certs/mosquitto-selfsigned.crt
14.2 Uppdatera Mosquitto-konfigurationen: Öppna mosquitto.conf och konfigurera för att använda WebSocket och SSL:
	sudo -i
	nano /etc/mosquitto/mosquitto.conf
	
	# Vanlig MQTT-anslutning utan TLS
	listener 1883
	protocol mqtt
	allow_anonymous true  # Eller "false" om du vill begränsa åtkomst

	# WebSocket med TLS för säker anslutning
	listener 9001
	protocol websockets
	cafile /etc/ssl/certs/mosquitto-selfsigned.crt
	keyfile /etc/ssl/private/mosquitto-selfsigned.key
	allow_anonymous false  # Rekommenderas för säkerhet, kräver autentisering
14.3 Starta om Mosquitto:
	sudo systemctl restart mosquito


5. Testa Lokalt Utan Internet
Verktyg för test: Använd kommandon som ping för att säkerställa att din Raspberry Pi och laptop kan kommunicera lokalt.
MQTT-anslutning: Kontrollera att MQTT-klienten kan publicera och prenumerera via WebSocket över TLS.
HTTPS-anslutning: På din laptop, navigera till https://192.168.0.129 och godkänn det självsignerade certifikatet för att komma åt Nginx-servern på Raspberry Pi.
Viktigt: Självsignerade Certifikat och VPN-behov
Eftersom självsignerade certifikat används här, kommer du att behöva bekräfta säkerheten på klientdatorn varje gång du besöker webbplatsen eller kopplar via VPN. Om du expanderar detta system senare, till exempel för fjärråtkomst över internet, rekommenderas att använda en certifikatutgivare som Let’s Encrypt och ställa in en extern VPN-server.












	