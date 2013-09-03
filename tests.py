from main import t, SessionNotFound, Session, root_logger
from nose.tools import raises
import unittest
import logging
from random import randint

root_logger.setLevel(logging.INFO)


def bootstrap():
    if t.has_clients():
        TEST_SESSION_PREFIX = 'tmxwrp_'

        # find current sessions prefixed with tmxwrp
        previous_sessions = [s.session_name for s in t.list_sessions()
                             if s.session_name.startswith(TEST_SESSION_PREFIX)]

        other_sessions = [s.session_name for s in t.list_sessions()
                          if not s.session_name.startswith(
                              TEST_SESSION_PREFIX
                          )]

        if not other_sessions:
            # create a test session so client won't close when other windows
            # cleaned up
            Session.new_session(session_name='test_' + str(randint(0, 1337)))
            Session.attached_pane().send_keys('created by tmuxwrapper tests.'
                                              ' you may delete this.',
                                              enter=False)
        else:
            t.switch_client(other_sessions[0])

        for session in previous_sessions:
            t.kill_session(previous_sessions)

        TEST_SESSION_NAME = TEST_SESSION_PREFIX + str(randint(0, 1337))

        session = Session.new_session(
            session_name=TEST_SESSION_NAME,
            kill_session=True
        )

        t.switch_client(TEST_SESSION_NAME)

        return (TEST_SESSION_NAME, session)


class TmuxTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            # atm bootstrap() retyrns name of session and the session object
            cls.TEST_SESSION_NAME, cls.session = bootstrap()
        except:
            cls.fail()
        return


class TestSessions(TmuxTest):
    '''
        self.session
            Session object
        self.TEST_SESSION_NAME
            string. name of the test case session.
    '''

    def tearDown(self):
        pass

    def test_has_session(self):
        assert t.has_session(self.TEST_SESSION_NAME) is True
        assert t.has_session('asdf2314324321') is False

    def test_3_switch_client_returns_session(self):
        '''
        switch_client should return reference to Session object
        '''
        pass


class WindowCreation(TmuxTest):

    def test_sync_windows(self):
        self.session.attached_window().select_layout('even-horizontal')
        self.session.attached_window().split_window()
        #session.sync_windows()
        self.session.attached_window().split_window('-h')

        self.session.select_window(1)

        self.session.attached_window().select_pane(1)
        self.session.attached_pane().send_keys('cd /srv/www/flaskr')
        self.session.attached_window().select_pane(0)
        self.session.attached_pane().send_keys('source .env/bin/activate')
        self.session.new_window('second')
        self.session.list_windows()
        #self.session.sync_windows()
        self.assertEqual(2, len(self.session._windows))
        self.session.new_window('testing 3')
        #self.session.sync_windows()
        self.session.list_windows()
        self.assertEqual(3, len(self.session._windows))
        self.session.select_window(1)
        self.session.kill_window(target_window='3')
        self.session.list_windows()
        #self.session.sync_windows()
        self.assertEqual(2, len(self.session._windows))
        #tmux('display-panes')


class WindowSelect(TmuxTest):
    def test_select_window(self):
        print self.session
        print self.session._windows
        self.session.new_window('testing 3')
        #self.session.sync_windows()
        self.session.list_windows()
        self.session.select_window(2)
        self.session.list_windows()
        self.assertEqual(2, int(self.session.attached_window()._TMUX['window_index']))

if __name__ == '__main__':

    if t.has_clients():
        unittest.main()
    else:
        print('must have a tmux client running')