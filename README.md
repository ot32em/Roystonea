Roystonea
=========

A Cloud Computing System with Pluggable Component Architecture.
Implemented via python script.


## Usage

* Step1: 
    Configure your system hierachy by xml file(see below).

* Step2: 
    royctl.py start [hierachy.xml]


## Hierachy XML


![Hierachy Diagram](http://cloud.github.com/downloads/ot32em/Roystonea/hierachy.png)
<Roystonea>
    <Coordinator host="140.112.5.1" port="500" />
    <Algorithm host="140.112.5.1" port="501" />
    <Coordinator host="140.112.5.1" port="502" />
    <Cloud host="140.112.1.1" port="100">
        <Cluster host="140.112.2.1" port="200">
            <Rack host="140.112.3.1" port="300">
                <Node host="140.112.4.1" port="400" />
                <Node host="140.112.4.2" port="400" />
            </Rack>
            <Rack host="140.112.3.2" port="300">
                <Node host="140.112.4.3" port="400" />
                <Node host="140.112.4.4" port="400" />
            </Rack>
        </Cluster>
    </Cloud>
</Roystonea>



