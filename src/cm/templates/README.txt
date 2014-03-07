Warning!
If you want to change any Libvirt XML templates, you should be aware. This may
cause vm or image fails at cloud code. If you use packages (apt-get or another)
remember, that all upgrades could override your changes. To avoid this, copy
whole directory to /etc/cc1/cm and update TEMPLATES directory list in
/usr/lib/cc1/cm/settings.py