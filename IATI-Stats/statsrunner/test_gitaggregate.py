import os
import imp
import shutil
import sys
from mock import patch


def test_gitaggregate(tmpdir):
    gitout = tmpdir.join('gitout')
    sys.argv = ['', '--dated']
    with patch.dict('os.environ', GITOUT_DIR=gitout.strpath):
        gitout.join('commits').join('AAA').join('aggregated').join('teststat.json').write('3', ensure=True)
        execfile('statsrunner/gitaggregate.py')
        assert gitout.join('gitaggregate').listdir() == [gitout.join('gitaggregate').join('teststat.json')]
        assert gitout.join('gitaggregate').join('teststat.json').read() == '{\n  "AAA": 3\n}'

        gitout.join('commits').join('BBB').join('aggregated').join('teststat.json').write('"test"', ensure=True)
        execfile('statsrunner/gitaggregate.py')
        assert gitout.join('gitaggregate').listdir() == [gitout.join('gitaggregate').join('teststat.json')]
        assert gitout.join('gitaggregate').join('teststat.json').read() == '{\n  "AAA": 3, \n  "BBB": "test"\n}'

        # Ensure that existing values are maintained once they are missing from the commits directory
        shutil.rmtree(gitout.join('commits').strpath)
        gitout.join('commits').join('CCC').join('aggregated').join('teststat.json').write('{}', ensure=True)
        execfile('statsrunner/gitaggregate.py')
        assert gitout.join('gitaggregate').listdir() == [gitout.join('gitaggregate').join('teststat.json')]
        assert gitout.join('gitaggregate').join('teststat.json').read() == '{\n  "AAA": 3, \n  "BBB": "test", \n  "CCC": {}\n}'


def test_gitaggregate_dated(tmpdir):
    gitout = tmpdir.join('gitout')
    sys.argv = ['', 'dated']
    with open('gitdate.json', 'w') as fp:
        fp.write('{"AAA":"1","BBB":"2","CCC":"3"}')
    with patch.dict('os.environ', GITOUT_DIR=gitout.strpath):
        gitout.join('commits').join('AAA').join('aggregated').join('teststat.json').write('3', ensure=True)
        execfile('statsrunner/gitaggregate.py')
        assert gitout.join('gitaggregate-dated').listdir() == [gitout.join('gitaggregate-dated').join('teststat.json')]
        assert gitout.join('gitaggregate-dated').join('teststat.json').read() == '{\n  "1": 3\n}'

        gitout.join('commits').join('BBB').join('aggregated').join('teststat.json').write('"test"', ensure=True)
        execfile('statsrunner/gitaggregate.py')
        assert gitout.join('gitaggregate-dated').listdir() == [gitout.join('gitaggregate-dated').join('teststat.json')]
        assert gitout.join('gitaggregate-dated').join('teststat.json').read() == '{\n  "1": 3, \n  "2": "test"\n}'

        # Ensure that existing values are maintained once they are missing from the commits directory
        shutil.rmtree(gitout.join('commits').strpath)
        gitout.join('commits').join('CCC').join('aggregated').join('teststat.json').write('{}', ensure=True)
        execfile('statsrunner/gitaggregate.py')
        assert gitout.join('gitaggregate-dated').listdir() == [gitout.join('gitaggregate-dated').join('teststat.json')]
        assert gitout.join('gitaggregate-dated').join('teststat.json').read() == '{\n  "1": 3, \n  "2": "test", \n  "3": {}\n}'


def test_gitaggregate_publisher(tmpdir):
    gitout = tmpdir.join('gitout')
    sys.argv = ['', '--dated']
    with patch.dict('os.environ', GITOUT_DIR=gitout.strpath):
        gitout.join('commits').join('AAA').join('aggregated-publisher').join('testpublisher').join('activities.json').write('3', ensure=True)
        execfile('statsrunner/gitaggregate-publisher.py')
        pubdir = gitout.join('gitaggregate-publisher').join('testpublisher')
        assert pubdir.listdir() == [pubdir.join('activities.json')]
        assert pubdir.join('activities.json').read() == '{\n  "AAA": 3\n}'

        gitout.join('commits').join('BBB').join('aggregated-publisher').join('testpublisher').join('activities.json').write('"test"', ensure=True)
        execfile('statsrunner/gitaggregate-publisher.py')
        pubdir = gitout.join('gitaggregate-publisher').join('testpublisher')
        assert pubdir.listdir() == [pubdir.join('activities.json')]
        assert pubdir.join('activities.json').read() == '{\n  "AAA": 3, \n  "BBB": "test"\n}'


        # Ensure that existing values are maintained once they are missing from the commits directory
        shutil.rmtree(gitout.join('commits').strpath)
        gitout.join('commits').join('CCC').join('aggregated-publisher').join('testpublisher').join('activities.json').write('{}', ensure=True)
        execfile('statsrunner/gitaggregate-publisher.py')
        pubdir = gitout.join('gitaggregate-publisher').join('testpublisher')
        assert pubdir.listdir() == [pubdir.join('activities.json')]
        assert pubdir.join('activities.json').read() == '{\n  "AAA": 3, \n  "BBB": "test", \n  "CCC": {}\n}'



def test_gitaggregate_publisher_dated(tmpdir):
    gitout = tmpdir.join('gitout')
    sys.argv = ['', 'dated']
    with open('gitdate.json', 'w') as fp:
        fp.write('{"AAA":"1","BBB":"2","CCC":"3"}')
    with patch.dict('os.environ', GITOUT_DIR=gitout.strpath):
        gitout.join('commits').join('AAA').join('aggregated-publisher').join('testpublisher').join('activities.json').write('3', ensure=True)
        execfile('statsrunner/gitaggregate-publisher.py')
        pubdir = gitout.join('gitaggregate-publisher-dated').join('testpublisher')
        assert pubdir.listdir() == [pubdir.join('activities.json')]
        assert pubdir.join('activities.json').read() == '{\n  "1": 3\n}'

        gitout.join('commits').join('BBB').join('aggregated-publisher').join('testpublisher').join('activities.json').write('"test"', ensure=True)
        execfile('statsrunner/gitaggregate-publisher.py')
        pubdir = gitout.join('gitaggregate-publisher-dated').join('testpublisher')
        assert pubdir.listdir() == [pubdir.join('activities.json')]
        assert pubdir.join('activities.json').read() == '{\n  "1": 3, \n  "2": "test"\n}'


        # Ensure that existing values are maintained once they are missing from the commits directory
        shutil.rmtree(gitout.join('commits').strpath)
        gitout.join('commits').join('CCC').join('aggregated-publisher').join('testpublisher').join('activities.json').write('{}', ensure=True)
        execfile('statsrunner/gitaggregate-publisher.py')
        pubdir = gitout.join('gitaggregate-publisher-dated').join('testpublisher')
        assert pubdir.listdir() == [pubdir.join('activities.json')]
        assert pubdir.join('activities.json').read() == '{\n  "1": 3, \n  "2": "test", \n  "3": {}\n}'
