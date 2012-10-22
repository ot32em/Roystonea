Roystonea
=========

A Cloud Computing System with Pluggable Component Architecture.
Implemented via python script.


## Daemons in system
*Coordinator - checking user input and operate corresponding action
*Subsystem Manager - update physical machine performance inforation in Database
*Algorithm - Provide fit location the virtual machine should locate


## Installation
in etc/default_cfg
```
install_dir = "/usr/share/roystonea/" # for a example
```
in every physical machine involving in Roystonea
you should place the roystonea package in install directory
```
# ls /usr/share/
Roystonea
```


## Usage
```
# cd /usr/share/roystonea
# ./royctl.py start [hierachy.xml]
```


## Hierachy XML Example
```
# ls
# hierachy.xml
```
![Hierachy Diagram](http://cloud.github.com/downloads/ot32em/Roystonea/hierachy2.png)


## License
    Roystonea - python implementation
    Copyright (C) 2012 NTU Parallel Lab

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.