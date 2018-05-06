import os,sys
old_path = sys.path

parentdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,parentdir) 

from _mm_client import MastermindClientTCP
from _mm_client import MastermindClientUDP

from _mm_server import MastermindServerTCP
from _mm_server import MastermindServerUDP
from _mm_server import MastermindServerCallbacksEcho
from _mm_server import MastermindServerCallbacksDebug

from _mm_errors import MastermindError
from _mm_errors import MastermindErrorClient
from _mm_errors import MastermindErrorServer
from _mm_errors import MastermindErrorSocket

from _mm_constants import MM_TCP,MM_UDP,MM_UNKNOWN

sys.path = old_path
