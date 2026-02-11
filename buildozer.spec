[app]
title = Diabetes-Kids-Quiz
package.name = diabetesquiz2026
package.domain = org.example

version = 1.0

source.dir = .
source.include_exts = py,html,css,js,png,svg,jpg,jpeg,gif,webp,csv,json,ico,woff,woff2,ttf,xml

# Wichtig: www/ muss rein!
source.include_patterns = www/*,www/**/*
icon.filename = %(source.dir)s/icon.png


requirements = python3,kivy,pyjnius


# optional, aber meistens angenehm:
fullscreen = 1

# Orientation: 'portrait', 'landscape' oder 'all' geht NICHT.
# Für frei drehbar macht man es über Manifest-Override (siehe unten).
orientation = portrait

android.api = 33
android.minapi = 21
android.ndk_api = 21

# Wenn du KEIN Internet brauchst, weglassen.
# Wenn du irgendwann online Ressourcen nachladen willst, setz INTERNET:
# android.manifest.application_arguments = android:usesCleartextTraffic="true"


android.manifest.application_arguments = android:networkSecurityConfig="@xml/network_security_config" android:usesCleartextTraffic="true"
android.permissions = INTERNET

# schöneres Log:
log_level = 2

[buildozer]
warn_on_root = 1

