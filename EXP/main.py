import os
import sys

from mangum import Mangum

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# current file directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from router import app  # noqa: E402

handler = Mangum(app)
