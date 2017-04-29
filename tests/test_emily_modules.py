"""Tests for Python modules in emily/emily_modules"""

import threading
import socket
import json
import sys
import os


from emily.emily_modules import sports
from emily.emily_modules import run_command
from emily.emily_modules import send_message
from emily.emily_modules import yes_no_parser
from emily.emily_modules import variables
from emily.emily_modules import utils
from emily.emily_modules import process_input
from emily.emily_modules import conversations
from emily.emily_modules import sessions


curdir = os.path.dirname(__file__)
data_dir = os.path.join(curdir,'data')


class CreateSocket(threading.Thread):
    """Test class for testing send_message module. Creates a socket to listen for messages."""
    def __init__(self,port):
        super(CreateSocket, self).__init__()
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('',port))
        self.s.listen(5)

    def run(self):
        while True:
            c,addr = self.s.accept()
            received = c.recv(4096)
            if sys.version_info >= (3,0):
                # In Python 3.x, the data transferred between sockets is in bytes
                received = received.replace(b'message',b'response')
            else:
                received = received.replace('message','response')
            c.send(received)
            c.close()
            self.s.close()
            break


class TestSports:
    """Tests for sports module which is used for documentation tutorials"""

    def test_baseball(self):
        """Does a sentence containing 'braves' return 'baseball' as the string and 'Braves' as the team?"""
        sport = sports.get_sport(user_input='I like the braves')
        assert sport['string'] == 'baseball'
        assert sport['team'] == 'Braves'

    def test_football(self):
        """Does a sentence containing 'falcons' return 'football' as the string and 'Falcons' as the team?"""
        sport = sports.get_sport(user_input='I like the falcons')
        assert sport['string'] == 'football'
        assert sport['team'] == 'Falcons'

    def test_unknown(self):
        """Does a sentence containing unknown team return 'unknown' as the string and team name as the team?"""
        sport = sports.get_sport(user_input='I like the mighty ducks')
        assert sport['string'] == 'unknown'
        assert sport['team'] == 'mighty ducks'

    def test_failure(self):
        """Does an unexpected sentence return 'unknown' as the string and the whole sentence as the team?"""
        sport = sports.get_sport(user_input='hello world')
        assert sport['string'] == 'unknown'
        assert sport['team'] == 'hello world'


class TestRunCommand:
    """The run_command module runs pieces of Python code and handles importing missing dependencies."""

    def test_run(self):
        """Does a command using an already imported module run correctly?"""
        result = run_command.run(command="datetime.strptime('03/17/2017','%m/%d/%Y').strftime('%Y%m%d')")
        assert result['success']
        assert result['response'] == '20170317'

    def test_re_run(self):
        """Does a command using a not-yet imported module run correctly?"""
        result = run_command.re_run(command="json.dumps({'foo':'bar'})",module='json')
        assert result['success']
        assert result['response'] == '{"foo": "bar"}'


class TestSendMessage:
    """The send_message module sends a JSON string containing 'message' and 'session_id' to a listening socket and expects one with 'response' and 'session_id' in return. Python values are returned, not the JSON string."""

    def test_send(self):
        """Using the CreateSocket class as a listener, does send_message.send() receive a response and session ID when a message and session ID are passed in?"""
        session = CreateSocket(port=8002)
        session.start()
        response,session_id = send_message.send(message='hello',session_id=123,port=8002)
        assert response == 'hello'
        assert session_id == 123


class TestYesNoParser:
    """The yes_no_parser module is used for yes_no_logic conversation nodes"""

    def test_check_input_yes(self):
        """Is 'Yeah' recognized as a 'yes' response?"""
        results = yes_no_parser.check_input(user_input='Yeah')
        assert results['result'] == 'yes'

    def test_check_input_no(self):
        """Is 'Nah' recognized as a 'no' response?"""
        results = yes_no_parser.check_input(user_input='Nah')
        assert results['result'] == 'no'

    def test_check_input_yes_prime(self):
        """Is 'Yes, <other_stuff>' recognized as a 'yes_prime' response?"""
        results = yes_no_parser.check_input(user_input='Yes, but I have something else to say')
        assert results['result'] == 'yes_prime'
        assert results['user_input'].lower() == 'but i have something else to say'

    def test_check_input_no_prime(self):
        """Is 'No, <other_stuff>' recognized as a 'no_prime' response?"""
        results = yes_no_parser.check_input(user_input='No, but I have something else to say')
        assert results['result'] == 'no_prime'
        assert results['user_input'].lower() == 'but i have something else to say'

    def test_check_input_unknown(self):
        """Does a non-yes/no answer yeild a None response?"""
        results = yes_no_parser.check_input(user_input='bananas')
        assert results['result'] is None


class TestVariables:
    """The variables module helps manage variable replacements in paterns, utterances, commands, and responses"""

    def test_check_stars(self):
        """Given an input that matches a pattern with a star, does check_stars add a 'star1' variable to session_variables without changing existing variables?"""
        session_vars = variables.check_stars(pattern='hello *',user_input='hello world',session_vars={'foo':'bar'})
        assert session_vars['foo'] == 'bar'
        assert session_vars['star1'] == 'world'

    def test_clear_stars(self):
        """Does clear_stars remove a 'starN' variable in session_variables without changing other variables?"""
        session_vars = variables.clear_stars(session_vars={'foo':'bar','star1':'world'})
        assert session_vars['foo'] == 'bar'
        assert 'star1' not in session_vars

    def test_set_vars(self):
        """Does set_vars add new variables to session_vars without changing existing variables?"""
        session_vars = variables.set_vars(session_vars={'foo':'bar'},template={'vars':[{'name':'hello','value':'world'}]})
        assert session_vars['foo'] == 'bar'
        assert session_vars['hello'] == 'world'

    def test_reset_vars(self):
        """Does reset_vars remove a non-reserved variable from session_vars?"""
        session_vars = variables.reset_vars(session_vars={'foo':'bar'},template={'reset':['foo']},key='reset')
        assert 'foo' not in session_vars

    def test_reset_vars_convo(self):
        """Does reset_vars set 'conversation' to 'default'?"""
        session_vars = variables.reset_vars(session_vars={'conversation':'other'},template={'reset':['conversation']},key='reset')
        assert session_vars['conversation'] == 'default'

    def test_reset_vars_all(self):
        """Does reset_vars set session_vars = session_vars['default_session_vars'] and still maintain 'default_session_vars' attribute?"""
        session_vars = variables.reset_vars(session_vars={'hello':'world','default_session_vars':{'foo':'bar'}},template={'reset':['all']},key='reset')
        assert session_vars['foo'] == 'bar'
        assert session_vars['default_session_vars'] == {'foo':'bar'}

    def test_replace_vars_var(self):
        """Does replace_vars replace variable name contained in curly brackets with variable value?"""
        response = variables.replace_vars(session_vars={'foo':'bar'},response="foo = {foo}")
        assert response == "foo = bar"

    def test_replace_vars_star(self):
        """Does replace_vars replace number 'N' contained in curly brackets with 'starN' value?"""
        response = variables.replace_vars(session_vars={'foo':'bar','star1':'hello'},response="* = {1}")
        assert response == "* = hello"        


class TestUtils:
    """The utils module is used to load brain files and remove punctuation from inputs."""

    def test_remove_punctuation(self):
        """Does remove_punctuation remove all punctuation?"""
        result = utils.remove_punctuation(input_string="Hello, World!")
        assert result == "Hello World"

    def test_remove_punctuation_stars(self):
        """Does remove_punctuation remove all punctuation except for '*'s when keep_stars is True?"""
        result = utils.remove_punctuation(input_string="Hello, *!",keep_stars=True)
        assert result == "Hello *"

    def test_load_data_json(self):
        """Does load_data load 'EMILY_DIR/tests/data/tests.json' correctly?"""
        brain = utils.load_data(brain_files=[os.path.join(data_dir,'tests.json')],source='LOCAL')
        assert brain['patterns']['tests.default'][0][0] == u'hello'
        assert brain['nodes']['tests.default.test_node']['responses'][0] == u'world'

    def test_load_data_yaml(self):
        """Does load_data load 'EMILY_DIR/tests/data/tests.yaml' correctly?"""
        brain = utils.load_data(brain_files=[os.path.join(data_dir,'tests.yaml')],source='LOCAL')
        assert brain['patterns']['tests.default'][0][0] == u'hello'
        assert brain['nodes']['tests.default.test_node']['responses'][0] == u'world'


class TestProcessInput:
    """The process_input module uses data from brain files to determine which node to process"""

    def test_score_matches_default(self):
        """Does a 'default' tuple beat a 'convo_default' tuple when the convo_default pattern is '*'?"""
        best_match = process_input.score_matches(default=(170.0,u'hello',u'other.default.test_node'),convo_default=(100.0,u'*',u'tests.default.other_node'),convo=None)
        assert best_match == (170.0,u'hello',u'other.default.test_node')

    def test_score_matches_convo_default(self):
        """Does a 'convo_default' tuple beat a 'default' tuple when the convo_default pattern is not a '*'?"""
        best_match = process_input.score_matches(default=(170.0,u'hello',u'other.default.test_node'),convo_default=(170.0,u'hello',u'tests.default.test_node'),convo=None)
        assert best_match == (170.0,u'hello',u'tests.default.test_node')

    def test_score_matches_convo(self):
        """Does a 'convo' tuple beat both 'default' and 'convo_default'?"""
        best_match = process_input.score_matches(default=(170.0,u'hello',u'other.default.test_node'),convo_default=(170.0,u'hello',u'tests.default.test_node'),convo=(170.0,u'hello',u'tests.other_convo.other_node'))
        assert best_match == (170.0,u'hello',u'tests.other_convo.other_node')

    def test_score_patterns_1(self):
        """Does an exact pattern match beat everything?"""
        best_match = process_input.score_patterns(user_input="hello world",search_patterns=[("hello world","null"),("hello wirld","null"),("hello *","null"),("*","null")],r_weight=1,pr_weight=0.7)
        assert best_match[1] == "hello world"

    def test_score_patterns_2(self):
        """Does a slightly different pattern match beat all non-exact matches?"""
        best_match = process_input.score_patterns(user_input="hello world",search_patterns=[("hello wirld","null"),("hello *","null"),("*","null")],r_weight=1,pr_weight=0.7)
        assert best_match[1] == "hello wirld"

    def test_score_patterns_3(self):
        """Does a partial star pattern match beat a catch-all match?"""
        best_match = process_input.score_patterns(user_input="hello world",search_patterns=[("hello *","null"),("*","null")],r_weight=1,pr_weight=0.7)
        assert best_match[1] == "hello *"

    def test_score_patterns_4(self):
        """Does a catch-all pattern match win when there's nothing better?"""
        best_match = process_input.score_patterns(user_input="hello world",search_patterns=[("*","null")],r_weight=1,pr_weight=0.7)
        assert best_match[1] == "*"

    def test_score_patterns_5(self):
        """Does a completely different pattern return a best match of None?"""
        best_match = process_input.score_patterns(user_input="hello world",search_patterns=[("bananas","null")],r_weight=1,pr_weight=0.7)
        assert best_match is None

    def test_match_patterns_1(self):
        """Does and exact pattern get matched?"""
        user_input = "hello world"
        patterns = {'tests.default': [(u'hello', 'tests.default.test_node'),(u'hello world', 'tests.default.test_node_2')]}
        conversation = 'default'
        session_vars = {'foo':'bar','hello':'world'}
        best_match = process_input.match_patterns(user_input=user_input,patterns=patterns,conversation=conversation,session_vars=session_vars)
        assert best_match[2] == u'tests.default.test_node_2'

    def test_match_patterns_2(self):
        """Does a pattern with variable replacement get matched?"""
        user_input = "hello world"
        patterns = {'tests.default': [(u'hello', 'tests.default.test_node'),(u'hello {hello}', 'tests.default.test_node_2')]}
        conversation = 'default'
        session_vars = {'foo':'bar','hello':'world'}
        best_match = process_input.match_patterns(user_input=user_input,patterns=patterns,conversation=conversation,session_vars=session_vars)
        assert best_match[2] == u'tests.default.test_node_2'

    def test_match_input_1(self):
        """Does match_input return expected response and leave existing session variables untouched?"""
        user_input = "hello"
        brain = utils.load_data(brain_files=[os.path.join(data_dir,'tests.json')],source='LOCAL')
        session_vars = {'foo':'bar','conversation':'default'}
        response,session_vars = process_input.match_input(user_input=user_input,brain=brain,session_vars=session_vars,intent=None)
        assert response == 'world'
        assert session_vars == {'foo':'bar','conversation':'default','next_node':None}

    def test_match_input_2(self):
        """Does match_input return "I don't know" response when user input does not match anything and leave existing session variables untouched?"""
        user_input = "hello world"
        brain = utils.load_data(brain_files=[os.path.join(data_dir,'tests.json')],source='LOCAL')
        session_vars = {'foo':'bar','conversation':'default'}
        response,session_vars = process_input.match_input(user_input=user_input,brain=brain,session_vars=session_vars,intent=None)
        assert response == "I'm sorry, I don't know what you are asking."
        assert session_vars == {'foo':'bar','conversation':'default','next_node':None}


class TestConversations:
    """The conversations module processes conversation nodes and executes necessary logic"""

    def test_response_node_1(self):
        """Does response_node return a random response from list of responses?"""
        response_options = ['a','b','c']
        node = {'node_type':'response','responses':response_options}
        session_vars = {'foo':'bar'}
        responses,session_vars,success = conversations.response_node(node=node,session_vars=session_vars,responses=[])
        assert success
        assert responses[0] in response_options

    def test_response_node_2(self):
        """Does response_node return a variable response with the appropriate value?"""
        node = {'node_type':'response','responses':['foo = {foo}']}
        session_vars = {'foo':'bar'}
        responses,session_vars,success = conversations.response_node(node=node,session_vars=session_vars,responses=[])
        assert success
        assert responses[0] == 'foo = bar'

    def test_router_node_1(self):
        """Does router_node choose next node at random from 'node_options' attribute?"""
        node_options = ['tests.default.a','tests.default.b']
        node = {'node_type':'router','node_options':node_options}
        next_node,success = conversations.router_node(node=node)
        assert success
        assert next_node in node_options

    def test_router_node_2(self):
        """Does router_node use value of 'next_node' as next node?"""
        node = {'node_type':'router','next_node':'tests.default.a'}
        next_node,success = conversations.router_node(node=node)
        assert success
        assert next_node == 'tests.default.a'

    def test_simple_logic_node(self):
        """Does simple_logic_node execute a command successfully and save dictionary values to session_vars?"""
        command = 'json.loads(\'{"foo":"bar","input":"{user_input}"}\')'
        node = {'node_type':'simple_logic','command':command}
        user_input = 'bananas'
        session_vars = {'hello':'world','user_input':user_input}
        session_vars,success = conversations.simple_logic_node(node=node,session_vars=session_vars,user_input=user_input)
        assert success
        assert session_vars['foo'] == 'bar'
        assert session_vars['input'] == 'bananas'

    def test_yes_no_logic_node(self):
        """Does yes_no_logic_node successfully call yes_no_parser and return matching node result?"""
        node = {'node_type':'yes_no_logic',
            'yes_node':'tests.default.yes',
            'yes_prime_node':'tests.default.yes_prime',
            'no_node':'tests.default.no',
            'no_prime_node':'tests.default.no_prime',
            'unknown_node':'tests.default.unknown'}
        user_input = "Yep"
        next_node,success = conversations.yes_no_logic_node(node=node,user_input=user_input)
        assert success
        assert next_node == 'tests.default.yes'

    def test_string_logic_node(self):
        """Does string_logic_node execute command successfully and match 'string' attribute to node attribute?"""
        command = 'json.loads(\'{"string":"bananas","input":"{user_input}"}\')'
        node = {'node_type':'string_logic',
            'command':command,
            'bananas':'tests.default.bananas',
            'unknown_node':'tests.default.unknown'}
        user_input = "hello world"
        session_vars = {'foo':'bar','user_input':user_input}
        next_node,success = conversations.string_logic_node(node=node,session_vars=session_vars,user_input=user_input)
        assert success
        assert next_node == 'tests.default.bananas'
        assert session_vars['input'] == 'hello world'

    def test_process_node(self):
        """Does process_node evaluate 'nodes[node_tag]' and return expected response?"""
        brain = utils.load_data(brain_files=[os.path.join(data_dir,'tests.json')],source='LOCAL')
        node_tag = "tests.default.test_node"
        session_vars = {'foo':'bar'}
        user_input = 'hello'
        responses,session_vars,conversation = conversations.process_node(node_tag=node_tag,nodes=brain['nodes'],session_vars=session_vars,responses=[],user_input=user_input)
        assert responses[0] == 'world'
        assert session_vars == {'foo':'bar','next_node':None}
        assert conversation == 'default'


class TestSessions:
    """The sessions module manages session variables in between code executions"""

    def test_get_session_count(self):
        """Does get_session_count return correct number of sessions from 'EMILY_DIR/tests/data/session_vars.json'?"""
        session_vars_path = os.path.join(data_dir,'session_vars.json')
        num_sessions = sessions.get_session_count(session_vars_path=session_vars_path)
        assert num_sessions == 1

    def test_get_session_vars(self):
        """Does get_session_vars return correct session variables from 'EMILY_DIR/tests/data/session_vars.json' when session ID exists?"""
        session_vars_path = os.path.join(data_dir,'session_vars.json')
        session_vars = sessions.get_session_vars(session_id=10000,source='LOCAL',session_vars_path=session_vars_path)
        assert session_vars['foo'] == 'bar'

    def test_create_new_session(self):
        """Does create_new_session create a new session in 'EMILY_DIR/tests/data/session_vars.json'?"""
        default_session_vars = {'conversation':'default'}
        session_vars_path = os.path.join(data_dir,'session_vars.json')
        session_id = sessions.create_new_session(default_session_vars=default_session_vars,source='LOCAL',session_vars_path=session_vars_path)
        num_sessions = sessions.get_session_count(session_vars_path=session_vars_path)
        assert session_id is not None
        assert num_sessions == 2

    def test_set_session_vars(self):
        """Does set_session_vars alter the new session created above in 'EMILY_DIR/tests/data/session_vars.json'?"""
        session_vars_path = os.path.join(data_dir,'session_vars.json')
        session_vars = {'conversation':'default',
            'default_session_vars': {'conversation':'default'},
            'hello':'world'}
        with open(os.path.join(data_dir,'session_vars.json'),'r') as f:
            all_vars = json.loads(f.read())
        session_id = None
        for s_id in all_vars:
            if s_id != '10000':
                session_id = int(s_id)
        sessions.set_session_vars(session_id=session_id,session_vars=session_vars,source='LOCAL',session_vars_path=session_vars_path)
        session_vars = sessions.get_session_vars(session_id=session_id,source='LOCAL',session_vars_path=session_vars_path)
        assert session_vars['hello'] == 'world'

    def test_remove_session(self):
        """Does remove_session successfully remove new session created above from 'EMILY_DIR/tests/data/session_vars.json'?"""
        session_vars_path = os.path.join(data_dir,'session_vars.json')
        with open(os.path.join(data_dir,'session_vars.json'),'r') as f:
            all_vars = json.loads(f.read())
        session_id = None
        for s_id in all_vars:
            if s_id != '10000':
                session_id = int(s_id)
        sessions.remove_session(session_id=session_id,source='LOCAL',session_vars_path=session_vars_path)
        num_sessions = sessions.get_session_count(session_vars_path=session_vars_path)
        assert num_sessions == 1
