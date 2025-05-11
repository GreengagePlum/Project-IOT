/*****************************
*
* 	Client MQTT sur esp32
* 	Contrôle led + envoie
*	status led, bouton et
*	photorésistance.
*
*	Basé sur le code d'adafruit:
*	https://github.com/adafruit/Adafruit_MQTT_Library
*	Et de Franck Wajsbürt
*	https://largo.lip6.fr/trac/sesi-peri
*
*
*****************************/

#include <SPI.h>
#include <Wire.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#include <string>

/* Librairies WiFi */
#include <WiFi.h>
#include "WiFiClientSecure.h"

/* Librairies MQTT */
#include "Adafruit_MQTT.h"
#include "Adafruit_MQTT_Client.h"


enum {STANDARD, MOUVEMENT}; // Type esp32



/******************** Configuration **********************/

/* Configuration ESP32
*
*	ESP_TYPE  : Type d'ESP32
*
*	STANDARD  = Avec Photo-Résistance
*	MOUVEMENT = Avec détecteur de mouvement
*
*/

#define ESP_TYPE STANDARD

/* Configuration WIFI
*
*	WLAN_SSID = Nom du réseau wifi (Doit étre 2.4 ghz)
*	WLAN_PASS = Mot de passe du réseau WIFI
*
*/

#define WLAN_SSID ""
#define WLAN_PASS ""


/* Configuration MQTT
*
*	MQTT_BROKER  = IP du broker MQTT
*	BROKER_PORT  = Port du broker MQTT
*	ID_ESP 		 = ID de l'esp32 (Pour MQTT)
*
*/

#define MQTT_BROKER      "192.168.137.241"   // ip raspberry

#define BROKER_PORT  1883 // port serveur raspberry

#define ID_ESP ""

#define FEED_LEDCOMMAND "led/command"  //IN

#define FEED_LEDSTATUS "led/status"	//OUT
#define FEED_BUTTONSTATUS "button/status"	//OUT
#define FEED_PHOTOSTATUS "photoresistor/status" //OUT


#define FEED_STATEJOIN "state/join"	//OUT
#define FEED_STATELEAVE "state/leave"	//OUT
#define FEED_STATENAME "state/nameAssign"	//IN


/******************** Configuration **********************/



// Adafruit IO Account Configuration
// (to obtain these values, visit https://io.adafruit.com and click on Active Key)


/************ Global State (you don't need to change this!) ******************/

// WiFiFlientSecure for SSL/TLS support



WiFiClient client; // ne pas utiliser la version secure
Adafruit_MQTT_Client mqtt(&client, MQTT_BROKER, BROKER_PORT, ID_ESP, "");

Adafruit_MQTT_Subscribe led_cmd = Adafruit_MQTT_Subscribe(&mqtt, ID_ESP FEED_LEDCOMMAND, 1); // doit étre 1
Adafruit_MQTT_Subscribe name_ass = Adafruit_MQTT_Subscribe(&mqtt, ID_ESP FEED_STATENAME, 0);

Adafruit_MQTT_Publish led_status = Adafruit_MQTT_Publish(&mqtt, ID_ESP FEED_LEDSTATUS,1);
Adafruit_MQTT_Publish bt_status = Adafruit_MQTT_Publish(&mqtt, ID_ESP FEED_BUTTONSTATUS,0);
Adafruit_MQTT_Publish pr_status = Adafruit_MQTT_Publish(&mqtt, ID_ESP FEED_PHOTOSTATUS,0);

Adafruit_MQTT_Publish st_join = Adafruit_MQTT_Publish(&mqtt, ID_ESP FEED_STATEJOIN,0);
Adafruit_MQTT_Publish st_leave = Adafruit_MQTT_Publish(&mqtt, ID_ESP FEED_STATELEAVE,0);

char * name_esp; 		// Uniquement pour le test, normalement remplacé aprés reception du message nameAssign
int lg_name_esp = 0;	// Longeur de la chaine

char * session;
int lg_session = 0;

bool pre_led;	// Etat led
int pre_bp;		// Etat bp

char mac[18];  // Adresse MAC


int x = 0;

/********************** Structures ***********************/

struct Timer {
  int timer;
  unsigned long period;
} ;


/********************** Structures ***********************/



/***************** Fonctions Auxiliaires *******************/

/* fontion lum et motion
*
*  int lum()	 : retourne la valeur de la photorésistance
*  bool motion() : retourne la valeur du détecteur de mouvement
*
*/

int lum(){
  return analogRead(36);
  }

 bool motion(){
  return digitalRead(13);
  }

#define MAX_WAIT_FOR_TIMER 2
unsigned int waitFor(int timer, unsigned long period){
  // code Franck
  static unsigned long waitForTimer[MAX_WAIT_FOR_TIMER];  // il y a autant de timers que de tâches périodiques
  unsigned long newTime = micros() / period;              // numéro de la période modulo 2^32
  int delta = newTime - waitForTimer[timer];              // delta entre la période courante et celle enregistrée
  if ( delta < 0 ) delta = 1 + newTime;                   // en cas de dépassement du nombre de périodes possibles sur 2^32
  if ( delta ) waitForTimer[timer] = newTime;             // enregistrement du nouveau numéro de période
  return delta;
}


void MQTT_connect() {
  int8_t ret;
  // Code Adafruit

  // Stop if already connected.
  if (mqtt.connected()) {
	return;
  }

  Serial.print("Connecting to MQTT... ");

  uint8_t retries = 3;
  while ((ret = mqtt.connect()) != 0) { // connect will return 0 for connected
	   Serial.println(mqtt.connectErrorString(ret));
	   Serial.println("Retrying MQTT connection in 5 seconds...");
	   mqtt.disconnect();
	   delay(5000);  // wait 5 seconds
	   retries--;
	   if (retries == 0) {
		 // basically die and wait for WDT to reset me
		 while (1);
	   }
  }

  Serial.println("MQTT Connected!");
}

void MQTT_send(Adafruit_MQTT_Publish * feed, const char * mess){
  if (! feed->publish(mess))
	Serial.println(F("Erreur d'envoie"));
  else
	Serial.println(F("OK!"));

}

// void alarm(){
//   tone(17, 440);
//   delay(500);
//   noTone(17);

// }

#define TOKEN ";"

void set_name(char * message, uint16_t len){
  // DANS CETTE FONCTION LES STRCPY SONT DELIBERES CAR STRNCPY COPIES TROP
	Serial.println("SET-NAME()");

	if (!strcmp(strtok(message,TOKEN),mac)){
		char * tmp_name = strtok(NULL,TOKEN);
		char * tmp_sess = strtok(NULL,TOKEN);

		if(tmp_name && tmp_sess){
			lg_name_esp = strlen(tmp_name);

			name_esp = (char*)malloc(lg_name_esp);
			if(name_esp){
				strcpy(name_esp,tmp_name);
			} else {
				Serial.println(F("Error set_name() name malloc"));
			}

			lg_session = strlen(tmp_sess);

			session = (char*)malloc(lg_session);
			if(session){
				strcpy(session,tmp_sess);
			} else {
				Serial.println(F("Error set_name() session malloc"));

			}
			Serial.print("\nname_esp\n");
			Serial.print(name_esp);
			Serial.print(strlen(name_esp));

			Serial.print("\nsession\n");
			Serial.print(session);
			Serial.print(strlen(session));

			}

	} else {
	  Serial.println(F("INCORRECT NAME"));
	}

}

void i_state_led(){
	int lg_led = (lg_name_esp + lg_session + 4);
	char * led = (char *)malloc(lg_led);

	Serial.println("i state led");

	if(led){
		snprintf(led,lg_led,"%s;%s;%d",name_esp,session,digitalRead(LED_BUILTIN));
		MQTT_send(&led_status,led);
		free(led);
	} else {
		  Serial.println(F("Error led message malloc"));
	}

}

void command_led(char * message, uint16_t len){
	Serial.println("command_led()");
	if (!strcmp(strtok(message,TOKEN),name_esp)){  	// si c'est le bon nom
		if(!strcmp(strtok(NULL,TOKEN),session)){	// et la bonne session
			bool val = atoi(strtok(NULL,TOKEN));

			pinMode(LED_BUILTIN,OUTPUT);
			digitalWrite(LED_BUILTIN, val);
			i_state_led();

		}
	}
}

bool set_lwt(){
	int jm_len = (lg_name_esp + lg_session + 2);
	char * join_mess = (char*)malloc(jm_len); // pas de free car utilisé par will

	if(join_mess){
		snprintf(join_mess,jm_len,"%s;%s",name_esp,session);

		//MQTT_send(&st_leave,join_mess);
		mqtt.disconnect();

		Serial.println("LTW Disconnect");

		delay(5000);
		mqtt.will(FEED_STATELEAVE, join_mess, 0, 0); //LWT

		mqtt.connect();
		MQTT_send(&st_join,join_mess);
		return 0;
	} else {
		Serial.println(F("Error join message malloc"));
		return 1;
	}

}

void i_state_photo(){
	int lg_photo = (lg_name_esp + lg_session + 5);
	char * photo = (char *)malloc(lg_photo);

	Serial.println("i state photo");

	if(photo){
		snprintf(photo,lg_photo,"%s;%s;%d",name_esp,session,(100-(lum()/41)));
		MQTT_send(&pr_status,photo);
		free(photo);
	} else {
		Serial.println(F("Error photo-resistor message malloc"));
	}
}
/***************** Fonctions Auxiliaires *******************/



/******************* Fonctions Setup *********************/

void mqtt_setup(){

  // BASE SUR LE CODE D'ADAFRUIT POUR ESP32

  Serial.begin(115200);

  pinMode(23,INPUT_PULLUP);
  pre_bp = !(digitalRead(23)); // inversion car pull-up

  delay(1000);

  WiFi.begin(WLAN_SSID, WLAN_PASS);
  delay(2000);

  while (WiFi.status() != WL_CONNECTED) {
	delay(500);
	Serial.print(".");
  }
  Serial.println();

  Serial.println("WiFi connected");

  // FIN WIFI DEBUT MQTT

	mqtt.setKeepAliveInterval(5);

  name_ass.setCallback(set_name);
  mqtt.subscribe(&name_ass);

  Serial.println("STARTUP\n");
  mqtt.connect();

  led_cmd.setCallback(command_led);
  mqtt.subscribe(&led_cmd);

  // envoie adresse MAC
  strncpy(mac,WiFi.macAddress().c_str(),18);

  Serial.println("MAC: ");
  Serial.println(mac);

  //Reception nom + session
  while(!lg_name_esp || !lg_session){
    Serial.println("Trying getting info ");
    MQTT_send(&st_join,mac);
    mqtt.processPackets(5000);
  }
  /* mqtt.processSubscriptionPacket(&name_ass); // Unstable */

  Serial.println("Start LWT");

  // LWT

  while(set_lwt()); // Boucle au cas ou malloc ne réussi pas 

  // command

  i_state_led();
  i_state_photo();
}

/******************* Fonctions Setup *********************/



/******************* Fonctions Loop **********************/


void bp_loop(struct Timer * clk) {
  if (!(waitFor(clk->timer,clk->period))) return;

  Serial.println("Loop BP\n");


  int lg_bp = (lg_name_esp + lg_session + 4);
  char * bp = (char *)malloc(lg_bp);

  Serial.println(pre_bp);
  Serial.println(!(digitalRead(23)));

	if(pre_bp == digitalRead(23)){ //inversé
		pre_bp = !(digitalRead(23));

		if(bp){
			snprintf(bp,lg_bp,"%s;%s;%d",name_esp,session,pre_bp);
			MQTT_send(&bt_status,bp);
			free(bp);
		} else {
			Serial.println(F("Error button message malloc"));
		}
	}

}


void mqtt_loop(struct Timer * clk) {
  if (!(waitFor(clk->timer,clk->period))) return;

  Serial.println("Loop MQTT\n");
  MQTT_connect();

  // Traitement des messages reçu
  mqtt.processPackets(1000);

  // photoresistor
  i_state_photo();
}

/******************* Fonctions Loop **********************/

struct Timer bp = {0,100000};
struct Timer mqtt_cli = {1,2000000};

void setup() {
  mqtt_setup();
}

void loop() {
  bp_loop(&bp);
  mqtt_loop(&mqtt_cli);
  //Serial.println(x++);
}
