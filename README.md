# WRecon 

WRecon is an open source no intussive web scanner. It is designed to discover all URL in a website recursively, without using bruteforce or unauthorized access. It comes with a camouflage engine and nice features for pentesting.

Screenshots
----

![Screenshot](https://raw.githubusercontent.com/fabiodelgadopereira/wrecon/master/Assets/screenshot.png)

Installation
----

You can download WRecon by cloning the [Git](https://github.com/fabiodelgadopereira/wrecon) repository:

    git clone https://github.com/fabiodelgadopereira/wrecon.git 

WRecon works out of the box with [Python](http://www.python.org/download/) version **3.x** on any platform.

Usage
----

To get a list of basic options and switches use:

    python wrecon.py -h

Simple usage:

    python wrecon.py -u http://target -r 1
