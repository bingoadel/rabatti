# ==============================================================================
# AUTOMATISCHES DJANGO DOCKER DEPLOYMENT-SKRIPT (LOKALER BAU)
# ==============================================================================
# Dieses Skript baut das Docker-Image lokal, verpackt es, lädt es auf den
# Ionos-Server hoch und gibt die finalen Befehle für den Server aus.
# ==============================================================================

# --- SCHRITT 0: KONFIGURATION (Bitte hier Ihre Daten eintragen) ---
$SERVER_IP   = "87.106.41.173"          # Die IP-Adresse Ihres Ionos-Servers
$SERVER_USER = "root"                   # Der SSH-Benutzername (meistens root)
$IMAGE_NAME  = "django-prod"            # Name für Ihr Docker-Image
$TARGET_DIR  = "/var/www"               # Zielordner auf dem Server

# Interne Variablen definieren
$TAR_FILE   = "${IMAGE_NAME}.tar"
$SSH_TARGET = "${SERVER_USER}@${SERVER_IP}"

# Immer aus dem Projektordner bauen, auch bei Doppelklick / "Mit PowerShell ausführen"
$RepoRoot = $PSScriptRoot
if ((Split-Path -Leaf $RepoRoot) -eq "Tools") {
    $RepoRoot = Split-Path -Parent $RepoRoot
}
Set-Location $RepoRoot

$exitCode = 0

function Wait-ForClose {
    Write-Host ""
    Read-Host "Enter druecken, um das Fenster zu schliessen"
}

try {
    Clear-Host
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host " STARTING DEPLOYMENT FOR: $IMAGE_NAME" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "Projektordner: $RepoRoot" -ForegroundColor Gray

    # --- SCHRITT 1: LOKALES DOCKER IMAGE BAUEN ---
    Write-Host "`n[1/4] Baue Docker Image lokal..." -ForegroundColor Yellow
    docker build -t "${IMAGE_NAME}:latest" .

    if ($LASTEXITCODE -ne 0) {
        throw "Fehler beim Bauen des Docker-Images. Skript abgebrochen."
    }
    Write-Host "OK Image erfolgreich gebaut." -ForegroundColor Green

    # --- SCHRITT 2: IMAGE ALS TAR-ARCHIV SPEICHERN ---
    Write-Host "`n[2/4] Exportiere Image als $TAR_FILE..." -ForegroundColor Yellow
    if (Test-Path $TAR_FILE) { Remove-Item $TAR_FILE }
    docker save -o $TAR_FILE "${IMAGE_NAME}:latest"

    if ($LASTEXITCODE -ne 0) {
        throw "Fehler beim Exportieren des Images. Skript abgebrochen."
    }
    Write-Host "OK Image erfolgreich als TAR gespeichert." -ForegroundColor Green

    # --- SCHRITT 3: TAR-DATEI AUF DEN SERVER HOCHLADEN ---
    Write-Host "`n[3/4] Uebertrage Datei auf den Ionos-Server ($SERVER_IP)..." -ForegroundColor Yellow
    Write-Host "Hinweis: Sie muessen gleich eventuell Ihr SSH-Passwort eingeben." -ForegroundColor Gray
    scp $TAR_FILE "${SSH_TARGET}:${TARGET_DIR}/"

    if ($LASTEXITCODE -ne 0) {
        throw "Fehler beim Hochladen der Datei. Skript abgebrochen."
    }
    Write-Host "OK Datei erfolgreich hochgeladen." -ForegroundColor Green

    # --- SCHRITT 4: LOKALE AUFRAEUMARBEITEN ---
    Write-Host "`n[4/4] Raeume lokale temporaere Dateien auf..." -ForegroundColor Yellow
    if (Test-Path $TAR_FILE) { Remove-Item $TAR_FILE }
    Write-Host "OK Lokale Bereinigung abgeschlossen." -ForegroundColor Green

    # --- FINALE ANWEISUNGEN FUER DEN SERVER ---
    Write-Host "`n==================================================" -ForegroundColor Green
    Write-Host " HOCHLADEN ERFOLGREICH! NAECHSTE SCHRITTE AUF DEM SERVER:" -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "1. Verbinden Sie sich per SSH mit Ihrem Server:"
    Write-Host "   ssh $SSH_TARGET" -ForegroundColor Cyan

    Write-Host "`n2. Fuehren Sie auf dem Server folgende Befehle aus:" -ForegroundColor Yellow
    Write-Host "   cd $TARGET_DIR"
    Write-Host "   docker load -i $TAR_FILE"
    Write-Host "   rm $TAR_FILE"

    Write-Host "`n3. Alten Container stoppen und neuen starten (falls vorhanden):" -ForegroundColor Yellow
    Write-Host "   docker stop django-backend 2>/dev/null; docker rm django-backend 2>/dev/null"
    Write-Host "   docker run -d --name django-backend --restart unless-stopped -p 127.0.0.1:8000:8000 -v ${TARGET_DIR}/django-static:/app/staticfiles ${IMAGE_NAME}:latest" -ForegroundColor Cyan

    Write-Host "`n4. Nginx neu starten (falls noch nicht konfiguriert):" -ForegroundColor Yellow
    Write-Host "   sudo systemctl restart nginx"
    Write-Host "==================================================" -ForegroundColor Green
}
catch {
    $exitCode = 1
    Write-Host ""
    Write-Host $_.Exception.Message -ForegroundColor Red
}
finally {
    Wait-ForClose
}

exit $exitCode
