#!/usr/bin/env python

"""A Python library for handling network address expansion (CIDR and dash notation)."""


from struct import unpack, pack
from socket import inet_pton, inet_ntop, AF_INET, AF_INET6


class Converter:
    """IP conversion methods to assisst with network expansion."""

    v4_MAX = 4294967295
    v6_MAX = 340282366920938463463374607431768211455

    def get_version(self, ip):
        """Fallback method to identify the IP version based on int size or oct/hextet delimeter."""
        if isinstance(ip, int):
            return 4 if 0 <= ip <= self.v4_MAX else 6
        elif isinstance(ip, str):
            return 4 if '.' in ip else 6
        return 4 # Fallback

    def v4_to_int(self, ip):
        """Calculate integer value for an IPv4 string."""
        try:
            return unpack('!L', inet_pton(AF_INET, ip))[0]
        except OSError:
            raise ValueError("illegal IP address %s" % ip)

    def v6_to_int(self, ip):
        """Calculate integer value for an IPv6 string."""
        try:
            hi,lo = unpack('!QQ', inet_pton(AF_INET6, ip))
            return (hi << 64) | lo
        except OSError:
            raise ValueError("illegal IP address %s" % ip)

    def int_to_v4(self, int_):
        """Convert integer to IPv4 string."""
        try:
            return inet_ntop(AF_INET, pack('!L', int_))
        except OSError:
            raise ValueError("illegal IP integer %d" % int_)

    def int_to_v6(self, int_):
        """Convert integer to IPv6 string."""
        try:
            return inet_ntop(AF_INET6, pack('!QQ', int_ >> 64, int_ & (2**64 - 1)))
        except OSError:
            raise ValueError("illegal IP integer %d" % int_)



class IPAddress(object):
    """Store IP address to represent as an int or string value."""

    converter = Converter()

    def __init__(self, ip, version=None):
        self.ip = ip
        self.version = version or self.converter.get_version(self.ip)
        self.int_ = int if self.version == 4 else long # Data type of int for IPv4 and long for IPv6
        self.to_int = self.converter.v4_to_int if self.version == 4 else self.converter.v6_to_int
        self.to_addr = self.converter.int_to_v4 if self.version == 4 else self.converter.int_to_v6

    def __int__(self):
        """Return the integer value of the IP address."""
        return self.to_int(self.ip) if isinstance(self.ip, str) else self.ip

    def __str__(self):
        """Return the string value of the IP address."""
        return self.to_addr(self.ip) if isinstance(self.ip, self.int_) else self.ip



class IPNetwork(object):
    """Store IP ranges using high and low IPs and calculating the in between."""

    converter = Converter()

    def __init__(self, network, version=None):
        self.network = network
        if not '/' in self.network:
            raise AttributeError("cidr identifying attribute missing '/'")

        self.version = version or self.converter.get_version(self.network)
        self.to_int = self.converter.v4_to_int if self.version == 4 else self.converter.v6_to_int
        self.bit = 32 if self.version == 4 else 128 # Maximum bits for a CIDR per IP version
        self.range = self.expand()

    def __len__(self):
        return ((self.range[1] + 1) - self.range[0])

    def __contains__(self, ip):
        if isinstance(ip, IPAddress):
            ip = int(ip)
        elif not isinstance(ip, int):
            ip = self.to_int(ip)
        return self.range[0] <= ip <= self.range[1]

    def __iter__(self):
        return self.iter_()

    def __getitem__(self, index):
        item = None

        if hasattr(index, 'indices'):
            (start, stop, step) = index.indices(self.__len__())

            if (start + step < 0) or (step > stop):
                item = [IPAddress(self.range[0], self.version)]

            else:
                start = self.range[0] + start
                stop = self.range[0] + stop
                item = [IPAddress(x, self.version) for x in range(start, stop, step)]

        else:
            try:
                index = int(index)

                if (-self.__len__()) <= index < 0:        # Negative index
                    item = IPAddress((self.range[1] + index + 1), self.version)

                elif 0 <= index <= (self.__len__() - 1):  # Positive or zero index
                    item = IPAddress((self.range[0] + index), self.version)

                else:
                    raise IndexError('index out range')

            except ValueError:
                raise TypeError('unsupported index type %r' % index)

        return item

    def expand(self):
        """ Expand a CIDR notation to the full range. """
        ip,cidr = self.network.split('/')
        if int(cidr) > self.bit:
            raise ValueError("invalid IPNetwork %s" % self.network)

        bits = self.bit - int(cidr)    # Max CIDR bits based on IP version
        ip   = self.to_int(ip)
        lo   = (ip >> bits) << bits
        hi   = lo | ((1 << bits) - 1)  # Subtract 1 to keep the range correct
        return (lo,hi)

    def iter_(self):
        start = self.range[0]
        stop  = self.range[1]
        index = 0

        while True:
            ip = start + index
            index += 1
            if ip > stop:
                break
            yield IPAddress(ip, self.version)  # Yield each IP address - this helps with memory



class IPRange(object):
    """Store IP ranges using high and low IPs and calculating the in between."""

    converter = Converter()

    def __init__(self, range_=None, start=None, stop=None, version=None):

        self.range_ = range_ or start # Use start to identify version, if not defined

        self.version = version or self.converter.get_version(self.range_)
        self.to_int = self.converter.v4_to_int if self.version == 4 else self.converter.v6_to_int

        if range_:
            if not '-' in range_:
                raise AttributeError("range identifying attribute missing '-'")
            self.range = self.expand()

        elif start and stop:
            self.range = (self.to_int(start.strip()), self.to_int(stop.strip()))

        else:
            raise ValueError("missing parameter for IPRange initialization")

    def __len__(self):
        return ((self.range[1] + 1) - self.range[0])

    def __contains__(self, ip):
        if isinstance(ip, IPAddress):
            ip = int(ip)
        elif not isinstance(ip, int):
            ip = self.to_int(ip)
        return self.range[0] <= ip <= self.range[1]

    def __iter__(self):
        return self.iter_()

    def __getitem__(self, index):
        item = None

        if hasattr(index, 'indices'):
            (start, stop, step) = index.indices(self.__len__())

            if (start + step < 0) or (step > stop):
                item = [IPAddress(self.range[0], self.version)]

            else:
                start = self.range[0] + start
                stop = self.range[0] + stop
                item = [IPAddress(x, self.version) for x in range(start, stop, step)]

        else:
            try:
                index = int(index)

                if (-self.__len__()) <= index < 0:        # Negative index
                    item = IPAddress((self.range[1] + index + 1), self.version)

                elif 0 <= index <= (self.__len__() - 1):  # Positive or zero index
                    item = IPAddress((self.range[0] + index), self.version)

                else:
                    raise IndexError('index out range')

            except ValueError:
                raise TypeError('unsupported index type %r' % index)

        return item

    def expand(self):
        """ Expand a dash notation to full range. """
        start,end = self.range_.split('-')
        lo = self.to_int(start.strip())
        hi = self.to_int(end.strip())
        if hi < lo:
            raise ValueError("lower bound IP greater than upper bound")

        return (lo,hi)

    def iter_(self):
        start = self.range[0]
        stop  = self.range[1]
        index = 0

        while True:
            ip = start + index
            index += 1
            if ip > stop:
                break
            yield IPAddress(ip, self.version)  # Yield each IP address - this helps with memory