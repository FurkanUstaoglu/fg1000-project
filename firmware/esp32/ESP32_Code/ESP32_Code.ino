//=====================================================
// ESP32 - WiFi Web Server (RCWS KONTROL)
//=====================================================

#include <WiFi.h>
#include <WebServer.h>

//=====================================================
// WiFi Ayarları (Access Point)
//=====================================================
const char* ssid = "RCWS_Kontrol";
const char* password = "12345678";

//=====================================================
// Web Server
//=====================================================
WebServer server(80);

//=====================================================
// Seri Haberleşme (Arduino Mega ile)
//=====================================================
#define RXD2 16   // ESP32 RX (Mega TX1 → pin 18)
#define TXD2 17   // ESP32 TX (Mega RX1 → pin 19)

//=====================================================
// SETUP
//=====================================================
void setup() {
  Serial.begin(115200);
  Serial2.begin(115200, SERIAL_8N1, RXD2, TXD2);
  
  delay(1000);
  Serial.println("=========================================");
  Serial.println("   RCWS - ESP32 KONTROL BIRIMI v3.2");
  Serial.println("=========================================");
  
  WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();
  Serial.print("Access Point IP Adresi: ");
  Serial.println(IP);
  Serial.print("SSID: "); Serial.println(ssid);
  Serial.print("Sifre: "); Serial.println(password);
  Serial.println("=========================================");
  Serial.println("Web Server baslatildi!");
  Serial.println("Tarayicidan su adrese git: http://" + IP.toString());
  Serial.println("=========================================");
  
  // Web sayfası route'ları
  server.on("/", handleRoot);
  server.on("/cmd/A", [](){ sendCommand('A'); });
  server.on("/cmd/B", [](){ sendCommand('B'); });
  server.on("/cmd/C", [](){ sendCommand('C'); });
  server.on("/cmd/D", [](){ sendCommand('D'); });
  server.on("/cmd/R", [](){ sendCommand('R'); });
  server.on("/cmd/L", [](){ sendCommand('L'); });
  server.on("/cmd/U", [](){ sendCommand('U'); });
  server.on("/cmd/W", [](){ sendCommand('W'); });
  server.on("/cmd/H", [](){ sendCommand('H'); });
  server.on("/cmd/M", [](){ sendCommand('M'); });
  server.on("/cmd/Z", [](){ sendCommand('Z'); });
  server.on("/cmd/T", [](){ sendCommand('T'); });
  server.on("/cmd/P", [](){ sendCommand('P'); });
  server.on("/cmd/S", [](){ sendCommand('S'); });
  
  server.begin();
}

//=====================================================
// LOOP
//=====================================================
void loop() {
  server.handleClient();
}

//=====================================================
// KOMUT GÖNDER (Arduino Mega'ya)
//=====================================================
void sendCommand(char cmd) {
  Serial.print("Komut gonderiliyor: ");
  Serial.println(cmd);
  
  Serial2.print(cmd);
  Serial2.print('\n');
  
  server.send(200, "text/plain", "Komut: " + String(cmd));
}

//=====================================================
// WEB SAYFASI (GÜNCELLENMİŞ ŞIK TASARIM)
//=====================================================
void handleRoot() {
  String html = R"rawliteral(
  <!DOCTYPE html>
  <html>
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RCWS Kontrol Paneli</title>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; user-select: none; }
      body {
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        background: #0a0e1a;
        color: #fff;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        margin: 0;
        padding: 16px;
      }
      .container {
        max-width: 480px;
        width: 100%;
        background: linear-gradient(145deg, #141b2d, #1a2338);
        border-radius: 28px;
        padding: 28px 24px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.8), inset 0 1px 0 rgba(255,255,255,0.05);
        border: 1px solid #2a3a5c;
        position: relative;
        overflow: hidden;
      }
      .container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(ellipse at 50% 0%, rgba(0, 180, 255, 0.03), transparent 60%);
        pointer-events: none;
      }
      .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        position: relative;
        z-index: 1;
      }
      .header h1 {
        font-size: 22px;
        font-weight: 700;
        background: linear-gradient(135deg, #00d4ff, #0088cc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px;
      }
      .header .badge {
        background: #00d4ff22;
        border: 1px solid #00d4ff44;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 10px;
        color: #64d4ff;
        letter-spacing: 1px;
      }
      .status-bar {
        background: #0d1424;
        padding: 12px 16px;
        border-radius: 14px;
        font-size: 13px;
        color: #64ffda;
        margin-bottom: 20px;
        border: 1px solid #233554;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        z-index: 1;
      }
      .status-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #64ffda;
        animation: pulse 1.5s ease-in-out infinite;
        margin-right: 8px;
      }
      @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.3; transform: scale(0.8); }
      }
      .section-title {
        font-size: 12px;
        font-weight: 600;
        color: #8892b0;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
        position: relative;
        z-index: 1;
      }
      .section-title .icon {
        font-size: 16px;
      }
      .btn-grid {
        display: grid;
        gap: 10px;
        margin-bottom: 16px;
        position: relative;
        z-index: 1;
      }
      .btn-grid-3 { grid-template-columns: repeat(3, 1fr); }
      .btn-grid-4 { grid-template-columns: repeat(4, 1fr); }
      .btn-grid-2 { grid-template-columns: 1fr 1fr; }
      
      .btn {
        background: #1a2744;
        border: none;
        padding: 14px 8px;
        border-radius: 12px;
        color: #ccd6f6;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.15s ease;
        box-shadow: 0 4px 0 #0d1424;
        text-align: center;
        border: 1px solid #233554;
        position: relative;
        overflow: hidden;
      }
      .btn:active {
        transform: translateY(4px);
        box-shadow: 0 2px 0 #0d1424;
      }
      .btn .sub {
        display: block;
        font-size: 9px;
        font-weight: 400;
        color: #8892b0;
        margin-top: 2px;
      }
      .btn-azimut { background: #1a2a4a; border-color: #2a4a6a; }
      .btn-azimut .sub { color: #64b5f6; }
      .btn-elevasyon { background: #2a1a3a; border-color: #4a2a5a; }
      .btn-elevasyon .sub { color: #ce93d8; }
      .btn-danger { background: #3d1a2a; border-color: #5c2a3a; color: #ff6b8a; }
      .btn-success { background: #1a3d2a; border-color: #2a5c3a; color: #64ff8a; }
      .btn-warning { background: #3d3a1a; border-color: #5c5a2a; color: #ffd64a; }
      .btn-info { background: #1a2a4a; border-color: #2a4a6a; color: #64d4ff; }
      .btn-full { grid-column: span 2; }
      
      .azimut-box { border-left: 3px solid #00d4ff; padding-left: 4px; margin-bottom: 12px; }
      .elevasyon-box { border-left: 3px solid #ce93d8; padding-left: 4px; margin-bottom: 12px; }
      
      .footer {
        text-align: center;
        font-size: 10px;
        color: #2a3a5c;
        margin-top: 16px;
        padding-top: 14px;
        border-top: 1px solid #1a2338;
        position: relative;
        z-index: 1;
      }
      
      @media (max-width: 480px) {
        .btn { padding: 12px 6px; font-size: 13px; }
        .container { padding: 20px 16px; }
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>⚡ RCWS</h1>
        <span class="badge">ONLINE</span>
      </div>
      
      <div class="status-bar" id="status">
        <span><span class="status-dot"></span> Sistem Aktif</span>
        <span id="posDisplay">0 / 0</span>
      </div>

      <!-- AZİMUT -->
      <div class="azimut-box">
        <div class="section-title"><span class="icon">⟳</span> AZİMUT</div>
        <div class="btn-grid btn-grid-3">
          <button class="btn btn-azimut" onclick="sendCmd('A')">+ Sağ <span class="sub">500</span></button>
          <button class="btn btn-azimut" onclick="sendCmd('R')">+2000 <span class="sub">büyük</span></button>
          <button class="btn btn-azimut" onclick="sendCmd('L')">-2000 <span class="sub">büyük</span></button>
          <button class="btn btn-azimut" onclick="sendCmd('B')">- Sol <span class="sub">500</span></button>
          <button class="btn btn-info" onclick="sendCmd('P')">📊 Konum</button>
          <button class="btn btn-success" onclick="sendCmd('H')">🏠 Home</button>
        </div>
      </div>

      <!-- ELEVASYON -->
      <div class="elevasyon-box">
        <div class="section-title"><span class="icon">↕</span> ELEVASYON</div>
        <div class="btn-grid btn-grid-3">
          <button class="btn btn-elevasyon" onclick="sendCmd('C')">+ Yukarı <span class="sub">500</span></button>
          <button class="btn btn-elevasyon" onclick="sendCmd('U')">+2000 <span class="sub">büyük</span></button>
          <button class="btn btn-elevasyon" onclick="sendCmd('W')">-2000 <span class="sub">büyük</span></button>
          <button class="btn btn-elevasyon" onclick="sendCmd('D')">- Aşağı <span class="sub">500</span></button>
          <button class="btn btn-warning" onclick="sendCmd('T')">🔄 Test</button>
          <button class="btn btn-danger" onclick="sendCmd('Z')">⚠ Sıfırla</button>
        </div>
      </div>

      <!-- SİSTEM BUTONLARI -->
      <div class="btn-grid btn-grid-3">
        <button class="btn btn-danger btn-full" onclick="sendCmd('S')">⏹ DURDUR</button>
        <button class="btn btn-info" onclick="sendCmd('M')">💾 Kaydet</button>
        <button class="btn btn-warning" onclick="sendCmd('P')">📊 Konum</button>
      </div>

      <div class="footer">
        RCWS v3.2 • EEPROM Hafızalı • WiFi Kontrol
      </div>
    </div>

    <script>
      function sendCmd(cmd) {
        const status = document.getElementById('status');
        status.innerHTML = '<span>⏳ Gönderiliyor...</span><span>' + cmd + '</span>';
        
        fetch('/cmd/' + cmd)
          .then(response => response.text())
          .then(data => {
            status.innerHTML = '<span><span class="status-dot"></span> ✅ ' + data + '</span><span id="posDisplay">✓</span>';
            setTimeout(() => {
              status.innerHTML = '<span><span class="status-dot"></span> Sistem Aktif</span><span id="posDisplay">0 / 0</span>';
            }, 1500);
          })
          .catch(error => {
            status.innerHTML = '<span>❌ Hata!</span><span>' + error + '</span>';
          });
      }
    </script>
  </body>
  </html>
  )rawliteral";
  
  server.send(200, "text/html", html);
}