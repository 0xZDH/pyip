# **PYIP Library**

This was just an experiment to see if I can expand IP ranges faster than the current implementations. This library doesnt handle anything outside of CIDR and dash notation expansion for IPv4/6. You can print IP Addresses as strings or their integer representation.

Currently works on Python 2 and 3.

## Usage

```
>>> # IPNetwork and IPRange objects are iterables of IPAddress objects
>>> 
>>> import pyip
>>> # Expand CIDR notation
>>> cidr = pyip.IPNetwork('192.168.0.0/24', version=4)
>>> # Get length of IP Network
>>> len(cidr)
256
>>> # Get string and integer representations of the first IP in the network
>>> str(cidr[0])
'192.168.0.0'
>>> int(cidr[0])
3232235520
>>> # Slice the IP Network list
>>> [str(x) for x in cidr[0:5]]
['192.168.0.0', '192.168.0.1', '192.168.0.2', '192.168.0.3', '192.168.0.4']
>>> # Check fo IPs in the IP Network
>>> '192.168.0.10' in cidr
True
>>> # Check for IPAddress object in IP Network
>>> pyip.IPAddress('192.168.0.10', version=4) in cidr
True
>>> # Check for IP integer in IP Network
>>> int(pyip.IPAddress('192.168.0.10', version=4)) in cidr
True



>>> # Test both range and start/stop IPRange objects
>>> range_ = pyip.IPRange(range_='192.168.0.0-192.168.0.255', version=4)
>>> range2 = pyip.IPRange(start='192.168.0.0', stop='192.168.0.255', version=4)
>>> # Length of IP Range
>>> len(range_)
256
>>> len(range2)
256
>>> # Get string and integer representations of the first IP in the range
>>> str(range_[0])
'192.168.0.0'
>>> str(range2[0])
'192.168.0.0'
>>> int(range_[0])
3232235520
>>> int(range2[0])
3232235520
>>> # Slice IP Range list
>>> [str(x) for x in range_[0:5]]
['192.168.0.0', '192.168.0.1', '192.168.0.2', '192.168.0.3', '192.168.0.4']
>>> [str(x) for x in range2[0:5]]
['192.168.0.0', '192.168.0.1', '192.168.0.2', '192.168.0.3', '192.168.0.4']
>>> # Check for IP string in range
>>> '192.168.0.10' in range_
True
>>> '192.168.0.10' in range2
True
>>> # Check for IPAddress objects in range
>>> pyip.IPAddress('192.168.0.10', version=4) in range_ 
True
>>> pyip.IPAddress('192.168.0.10', version=4) in range2
True
>>> # Check for IP integer in range
>>> int(pyip.IPAddress('192.168.0.10', version=4)) in range_
True
>>> int(pyip.IPAddress('192.168.0.10', version=4)) in range2
True



>>> # Handle a single IP Address
>>> ip = pyip.IPAddress('192.168.0.0', version=4)
>>> str(ip)
'192.168.0.0'
>>> int(ip)
3232235520



>>> # Loop through expanded network and write data to file
>>> for ip in pyip.IPNetwork('192.168.0.0/24'): 
...   file1.write("%s\n" % str(ip))
...   file2.write("%d\n" % int(ip))



>>> # Expand IPv6 CIDR
>>> ip6 = pyip.IPNetwork('2001:0db8:0000:0042:0000:8a2e:0370:7334/126', 6) 
>>> len(ip6)
4
>>> str(ip6[0])
'2001:db8:0:42:0:8a2e:370:7334'
>>> int(ip6[0])
42540766411282594074389245746715063092L
```

## Benchmarks

Benchmarks to test the speed of the 'pyip' expansions against the popular network library 'netaddr'.

### Loop through IP range:
```
>>> import timeit, pyip, netaddr
>>> 
>>> def test1():
...   for x in pyip.IPNetwork('3.0.0.0/20', 4):
...     y = str(x)
... 
>>> def test2():
...   for x in netaddr.IPNetwork('3.0.0.0/20'):
...     y = str(x)
... 
>>> timeit.timeit('test1()', setup='from __main__ import test1', number=100) # PYIP
0.5387578010559082
>>> timeit.timeit('test2()', setup='from __main__ import test2', number=100) # NETADDR
1.056675910949707
```

### Loop through IP range and write addresses to file:
```
>>> import netaddr, pyip, time
>>> 
>>> def test1():
...     start = time.time()
...     file_ = open('pyip.txt', 'w')
...     for x in pyip.IPNetwork('3.0.0.0/10', 4):
...             file_.write("%s\n" % str(x))
...     file_.close()
...     end = time.time() - start
...     print("TIME: %f" % end)
... 
>>> def test2():
...     start = time.time()
...     file_ = open('netaddr.txt', 'w')
...     for x in netaddr.IPNetwork('3.0.0.0/10'):
...             file_.write("%s\n" % str(x))
...     file_.close()
...     end = time.time() - start
...     print("TIME: %f" % end)
... 
>>> test1() # PYIP
TIME: 6.767779
>>> test2() # NETADDR
TIME: 13.749671
```

## TODO

* Add support for converting IP range/list to list of CIDRs (without overflow)
