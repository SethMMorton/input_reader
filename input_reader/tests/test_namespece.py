from input_reader import Namespace

def test_namespace_basic():
    ns1 = Namespace()
    assert not ns1
    assert len(ns1) == 0

    ns2 = Namespace()
    ns2.add('big', True)
    assert ns2
    assert len(ns2) == 1

    assert ns1 != ns2
    ns1.add('big', True)
    assert ns1 == ns2

def test_namespace_lists():
    ns1 = Namespace()
    ns1.add('big', True)
    ns1.add('small', False)
    ns1.add('medium', True)
    ns1.add('huge', False)
    assert ns1.keys() == ('big', 'small', 'medium', 'huge')
    assert ns1.make_set() == set(('big', 'small', 'medium', 'huge'))
    ns1.remove('small')
    assert ns1.keys() == ('big', 'medium', 'huge')
    assert ns1.values() == (True, True, False)
    assert ns1.items() == (('big', True), ('medium', True), ('huge', False))

def test_namespace_get():
    ns1 = Namespace()
    ns1.add('big', True)
    ns1.add('small', False)
    ns1.add('medium', True)
    ns1.add('huge', False)
    assert not ns1.get('huge')
    assert ns1.get('tiny') is None
    assert ns1.get('tiny', 'sally') == 'sally'

def test_namespace_contains():
    ns1 = Namespace()
    ns1.add('big', True)
    ns1.add('small', False)
    ns1.add('medium', True)
    ns1.add('huge', False)
    assert 'big' in ns1
    assert 'tiny' not in ns1

def test_namespace_string():
    ns1 = Namespace()
    ns1.add('big', True)
    ns1.add('small', False)
    ns1.add('medium', True)
    ns1.add('huge', False)
    assert str(ns1) == \
            'Namespace(big=True, small=False, medium=True, huge=False)'