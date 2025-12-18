== Ixontray
Small utility to connect quickly to a given ixon system.

== Installation
To install the application run:

=== Ubuntu 22.04
[source, bash]
----
sudo apt-get -qq install libegl1 libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxkbcommon-x11-0
pipx install ixontray
----


=== Ubuntu 20.04
[source, bash]
----
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.10
pipx install ixontray --python <path-to-python3.10>  #in my case: /usr/bin/python3.10
sudo apt-get -qq install libegl1 libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxkbcommon-x11-0
----

You can run the application:



[source, bash]
----
ixontray
----

Or run the laucher

[source, bash]
----
ixontray --launcher
----
TIP:: Best to add that to a system wide shortcut. I have it at `WIN+X` ( System Settings > Keyboard > Keyboard Shortcuts > Custom Shortcuts > Add a new one )

INFO:: The first time you will need to enter your login credentials in the window that will open.

NOTE:: You need to run the application first before you can run the launcher.

A tray icon like this will appear:

image::tray.png[]
