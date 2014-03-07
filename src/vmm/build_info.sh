#!/bin/bash

# Plik konfiguracyjny do budowania paczek. Jest uruchamiany w katalogu paczki i
# mozna korzystac w nim z lokalnych plikow. Skrypty budujace pakiety przeszukuja
# repozytorium w poszukiwaniu tych plikow i buduja tylko te pakiety.
#
# Plik ma forme skryptu bashowego. Niektore zmienne moga miec forme tablic,
#  ktore powinny miec format: LISTA=( "tekst1" "tekst2" ) Nalezy pamietac o
# braku przecinka pomiedzy kolejnymi elementami!


###############################################################################
#    Zmienne dla pliku DEBIAN/controll zawierajacego informacje o paczce      #
###############################################################################

PKG_SECTION="vm"

# Nazwa paczki. Jest to sklejanie z PACKAGE_PREFIX-NAZWA-PACKAGE_SUFFIX z config.sh
PACKAGE_NAME="ctx"

# Wersja paczki (format: czas_budowania)
VERSION=`date +"%Y%m%d%H%M%S"`

# Architektura docelowego systemu
ARCH="all"

# Opiekun paczki
MAINTAINER="Michał Szostak <szostak.m.f@gmail.pl>"

# Zaleznosci (format: nazwa_paczki (>= wymagana wersja) lub tylko nazwa_paczki)
DEPS="bash (>= 3.2-4), python (>= 2.6), python-openssl, openssl"
RECOMMENDS=""
CONFLICTS="cc1-system-rm-v1.4, cc1-system-rm-v1.5, cc1-system-cm-v1.6"

# Strona domowa paczki/projektu
HOMEPAGE="http://cc1.ifj.edu.pl"

# Sekcja, do ktorej ma zostac przypisana paczka (najlepiej main). Jest to
# podawane przy wpisie repozytorium w sources.list
SECTION="main"

# Okresla, czy paczka jest niezbedna do dzialania systemu (extra, optional,
# standard, important, required)
PRIORITY="optional"

# Krotki, jednoliniowy opis paczki
SHORT_DESC="Managment tools for virtual machines."

# Dlugi opis paczki. Kazda linia musi zaczynac sie od tabulatora!
DESC="Managment tools for virtual machines."


###############################################################################
#               Zmienne potrzebne do procesu budowania pakietu                #
###############################################################################

# Katalog z plikami konfiguracyjnymi (sciezka relatywna w katalogu pakietu)
CONF_FILES="config/"

# Pliki inicjalizujące pakiet (kopiowane do /etc/init.d)
INIT_SCRIPT="package/ctx"

# Skrypt paczki uruchamiany przed jej rozpakowaniem. Wywolywany jest z parame-
# trami:
# - install
# - upgrade
PREINST=""

# Skrypt paczki uruchamiany po jej zainstalowaniu. Konfiguruje caly pakiet. Na
# ogol uruchamiany z parametrem configure
POSTINST="package/postinst"

# Skrypt paczki uruchamiany przed jej usunieciem przez apt-get remove. O ile
# postinst jest wywolywane na ogol z parametrem configure, to prerm moze byc
# wywolany z nastepujacymi parametrami:
# - remove - przy apt-get remove
# - upgrade <wersja> - pakiet jest zastepywany jego nowsza wersja i stary prerm
#                      jest wykonywany
# - 
PRERM="package/prerm"

# Skrypt paczki uruchamiany po usunieciu paczki. Mozliwe parametry wywolania:
# - remove
# - purge - usuwanie wszystkich plikow konfiguracyjnych
# - upgrade - po usunieciu paczki i przed zastapieniem jej nowa
POSTRM="package/postrm"

# Plik templates zawierajacy wszystkie pytania potrzebne do skonfigurowania pakietu
TEMPLATES=""
