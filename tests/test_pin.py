from unittest import TestCase

from ddtrace import Pin
from nose.tools import eq_, ok_, assert_raises


class PinTestCase(TestCase):
    """TestCase for the `Pin` object that is used when an object is wrapped
    with our tracing functionalities.
    """
    def setUp(self):
        # define a simple class object
        class Obj(object):
            pass

        self.Obj = Obj

    def test_pin(self):
        # ensure a Pin can be attached to an instance
        obj = self.Obj()
        pin = Pin(service='metrics')
        pin.onto(obj)

        got = Pin.get_from(obj)
        eq_(got.service, pin.service)
        ok_(got is pin)

    def test_cant_pin_with_slots(self):
        # ensure a Pin can't be attached if the __slots__ is defined
        class Obj(object):
            __slots__ = ['value']

        obj = Obj()
        obj.value = 1

        Pin(service='metrics').onto(obj)
        got = Pin.get_from(obj)
        ok_(got is None)

    def test_cant_modify(self):
        # ensure a Pin is immutable once initialized
        pin = Pin(service='metrics')
        with assert_raises(AttributeError):
            pin.service = 'intake'

    def test_copy(self):
        # ensure a Pin is copied when using the clone methods
        p1 = Pin(service='metrics', app='flask', tags={'key': 'value'})
        p2 = p1.clone(service='intake')
        # values are the same
        eq_(p1.service, 'metrics')
        eq_(p2.service, 'intake')
        eq_(p1.app, 'flask')
        eq_(p2.app, 'flask')
        # but it's a copy
        ok_(p1.tags is not p2.tags)
        # of almost everything
        ok_(p1.tracer is p2.tracer)

    def test_none(self):
        # ensure get_from returns None if a Pin is not available
        ok_(Pin.get_from(None) is None)

    def test_repr(self):
        # ensure the service name is in the string representation of the Pin
        pin = Pin(service='metrics')
        ok_('metrics' in str(pin))

    def test_override(self):
        # ensure Override works for an instance object
        class A(object):
            pass

        Pin(service='metrics', app='flask').onto(A)
        a = A()
        Pin.override(a, app='django')
        eq_(Pin.get_from(a).app, 'django')
        eq_(Pin.get_from(a).service, 'metrics')

        b = A()
        eq_(Pin.get_from(b).app, 'flask')
        eq_(Pin.get_from(b).service, 'metrics')

    def test_override_missing(self):
        # ensure overriding an instance doesn't override the Class
        class A(object):
            pass

        a = A()
        ok_(Pin.get_from(a) is None)
        Pin.override(a, service='metrics')
        eq_(Pin.get_from(a).service, 'metrics')

        b = A()
        ok_(Pin.get_from(b) is None)
